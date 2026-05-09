"""HTTP endpoints for the webhooks app.

The single endpoint here, :func:`github_webhook`, accepts a POST from
GitHub at ``/webhooks/github`` and verifies the
``X-Hub-Signature-256: sha256=<hex>`` header against the configured
``GITHUB_WEBHOOK_SECRET``. Verified deliveries are persisted as
:class:`webhooks.models.WebhookEvent` rows; unsigned and wrong-signature
deliveries are rejected with HTTP 401 and intentionally not stored.
"""

from __future__ import annotations

import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import WebhookEvent


_SIGNATURE_HEADER = "X-Hub-Signature-256"
_EVENT_HEADER = "X-GitHub-Event"
_DELIVERY_HEADER = "X-GitHub-Delivery"
_SIGNATURE_PREFIX = "sha256="


def _expected_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return _SIGNATURE_PREFIX + digest


@csrf_exempt
@require_POST
def github_webhook(request: HttpRequest) -> JsonResponse:
    """Verify the HMAC SHA-256 signature and record the event.

    GitHub signs the request body with the shared secret and sends the
    digest in ``X-Hub-Signature-256``. We compute the same digest using
    :func:`hmac.compare_digest` to avoid the timing-side-channel that a
    naive ``==`` comparison would expose.
    """

    secret = getattr(settings, "GITHUB_WEBHOOK_SECRET", "") or ""
    provided = request.headers.get(_SIGNATURE_HEADER, "")
    if not provided.startswith(_SIGNATURE_PREFIX):
        return JsonResponse({"detail": "missing signature"}, status=401)

    expected = _expected_signature(secret, request.body)
    if not hmac.compare_digest(expected, provided):
        return JsonResponse({"detail": "invalid signature"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        # GitHub always sends JSON; record the raw body as a string fallback
        # so a debugging operator can still inspect the delivery.
        payload = {"raw": request.body.decode("utf-8", errors="replace")}

    WebhookEvent.objects.create(
        provider="github",
        event_type=request.headers.get(_EVENT_HEADER, ""),
        delivery_id=request.headers.get(_DELIVERY_HEADER, ""),
        payload=payload,
    )
    return JsonResponse({"detail": "accepted"}, status=202)
