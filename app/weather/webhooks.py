"""GitHub webhook handling."""
import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import WebhookEvent


def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature_header:
        return False

    hash_algorithm, github_signature = signature_header.split('=')
    if hash_algorithm != 'sha256':
        return False

    mac = hmac.new(secret.encode(), msg=payload_body, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, github_signature)


@csrf_exempt
@require_POST
def github_webhook(request: HttpRequest) -> HttpResponse:
    """Handle GitHub webhook events."""
    signature = request.headers.get('X-Hub-Signature-256', '')
    event_type = request.headers.get('X-GitHub-Event', '')
    delivery_id = request.headers.get('X-GitHub-Delivery', '')

    if not verify_signature(request.body, signature, settings.WEBHOOK_SECRET):
        return JsonResponse({'error': 'Invalid signature'}, status=403)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    if not delivery_id:
        return JsonResponse({'error': 'Missing delivery ID'}, status=400)

    if WebhookEvent.objects.filter(delivery_id=delivery_id).exists():
        return JsonResponse({'message': 'Event already processed'}, status=200)

    WebhookEvent.objects.create(
        event_type=event_type,
        payload=payload,
        signature=signature,
        delivery_id=delivery_id,
    )

    return JsonResponse({
        'message': 'Webhook received',
        'event_type': event_type,
        'delivery_id': delivery_id
    }, status=200)
