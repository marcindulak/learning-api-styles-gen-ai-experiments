"""GitHub webhook endpoint.

GitHub signs each delivery with HMAC SHA-256 over the raw request body
using the shared webhook secret and sends the result in the
X-Hub-Signature-256 header. Deliveries with a missing or invalid
signature are rejected.
"""
import hashlib
import hmac

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def _signature_is_valid(request):
    received = request.headers.get("X-Hub-Signature-256", "")
    digest = hmac.new(
        settings.WEBHOOK_SECRET.encode(), request.body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={digest}", received)


@csrf_exempt
@require_POST
def github_webhook(request):
    if not settings.WEBHOOK_SECRET or not _signature_is_valid(request):
        return JsonResponse({"detail": "invalid webhook signature"}, status=403)
    event = request.headers.get("X-GitHub-Event", "")
    if event == "ping":
        return JsonResponse({"message": "pong"})
    return JsonResponse({"message": f'event "{event}" accepted'})
