"""
GitHub webhook handler for receiving webhook events.
Validates HMAC-SHA256 signatures and logs events to WebhookEvent model.
"""
import hmac
import hashlib
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import WebhookEvent

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def github_webhook(request):
    """
    Handle GitHub webhook events.

    Validates HMAC-SHA256 signature from X-Hub-Signature-256 header.
    Stores event in WebhookEvent model.

    Returns:
        - 200 on success
        - 400 if signature header missing
        - 403 if signature validation fails
    """
    # Get the signature from headers
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return JsonResponse({'error': 'Missing X-Hub-Signature-256 header'}, status=400)

    # Get the event type
    event_type = request.headers.get('X-GitHub-Event', 'unknown')

    # Get the webhook secret
    webhook_secret = settings.WEBHOOK_SECRET
    if not webhook_secret:
        return JsonResponse({'error': 'Webhook secret not configured'}, status=500)

    # Get raw request body (bytes) for HMAC computation
    payload_bytes = request.body

    # Compute expected signature using raw bytes
    # GitHub signature format: sha256=hex_digest
    expected_signature = 'sha256=' + hmac.new(
        webhook_secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures using constant-time comparison
    if not hmac.compare_digest(signature, expected_signature):
        return JsonResponse({'error': 'Invalid signature'}, status=403)

    # Parse payload
    try:
        payload_json = json.loads(payload_bytes)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    # Store event in database
    try:
        WebhookEvent.objects.create(
            event_type=event_type,
            payload=payload_json,
            processed=False
        )
    except Exception as e:
        logger.exception('Failed to store webhook event')
        return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'status': 'received'}, status=200)
