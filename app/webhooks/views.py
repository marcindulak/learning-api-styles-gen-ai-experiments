import hashlib
import hmac
import json

from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GitHubWebhookEvent


class GitHubWebhookView(APIView):
    def post(self, request):
        signature_header = request.headers.get("X-Hub-Signature-256")
        if not signature_header or not self._signature_is_valid(request.body, signature_header):
            return Response({"errors": ["Invalid or missing signature."]}, status=401)

        delivery_id = request.headers.get("X-GitHub-Delivery", "")
        # GitHub redelivers the same event (same delivery id) when it doesn't
        # receive a timely acknowledgement, so a redelivery is expected,
        # normal traffic, not a client error: acknowledge it without
        # recording a duplicate. Checked before parsing the body so a
        # redelivery (the common case this branch exists for) skips the
        # JSON-decode work entirely, since its payload is discarded either way.
        if GitHubWebhookEvent.objects.filter(delivery_id=delivery_id).exists():
            return Response({"status": "accepted"}, status=200)

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"errors": ["Malformed JSON body."]}, status=400)

        # The exists() check above is a fast path only, not the correctness
        # guarantee: it can't close the gap between two truly concurrent
        # redeliveries both passing it before either creates a row. The
        # model's own delivery_id unique constraint is what actually
        # guarantees no duplicate is ever stored; catching the resulting
        # IntegrityError here (rather than letting it surface as a 500)
        # makes that guarantee atomic instead of a second, racy check.
        try:
            # Per Django's own transaction docs, catching IntegrityError must
            # wrap the failing statement in its own atomic() block -- without
            # it, a broken statement inside a larger transaction (e.g. a
            # future ATOMIC_REQUESTS=True or an enclosing atomic() block)
            # would poison every later query in that same transaction, not
            # just this one.
            with transaction.atomic():
                GitHubWebhookEvent.objects.create(
                    event_type=request.headers.get("X-GitHub-Event", ""),
                    delivery_id=delivery_id,
                    payload=payload,
                )
        except IntegrityError:
            pass
        return Response({"status": "accepted"}, status=200)

    @staticmethod
    def _signature_is_valid(body, signature_header):
        # Constant-time comparison (hmac.compare_digest) is required here to avoid
        # a timing side-channel that would let an attacker recover the digest
        # byte-by-byte from response-time differences.
        digest = hmac.new(settings.WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()
        expected_header = f"sha256={digest}"
        return hmac.compare_digest(expected_header, signature_header)
