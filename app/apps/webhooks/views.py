from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import hmac
import hashlib
from django.conf import settings
from .models import GitHubWebhook


def _validate_github_signature(payload_body, signature_header):
    """
    Validate GitHub webhook signature.
    """
    if not signature_header:
        return False

    # Get the secret from settings
    webhook_secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', None)
    if not webhook_secret:
        return False

    # GitHub sends signature as "sha256=<hash>"
    if not signature_header.startswith('sha256='):
        return False

    # Calculate the expected signature
    if isinstance(payload_body, str):
        payload_body = payload_body.encode('utf-8')

    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    # Compare with the provided signature
    provided_signature = signature_header[7:]  # Remove "sha256=" prefix
    return hmac.compare_digest(expected_signature, provided_signature)


def _validate_payload(payload):
    """
    Validate the webhook payload has required fields.
    """
    # For GitHub webhooks, we expect at least:
    # - repository: object with repository info
    # - action: string indicating the action
    # - pull_request, issues, push, etc.: the event data

    if not isinstance(payload, dict):
        return False

    # Check for repository field (present in most GitHub events)
    if 'repository' not in payload:
        return False

    # If it has pull_request, it should be a dict
    if 'pull_request' in payload:
        if not isinstance(payload['pull_request'], dict):
            return False

    return True


@csrf_exempt
@require_http_methods(["POST"])
def github_webhook(request):
    """
    Handle GitHub webhook events.
    """
    try:
        # Get the raw body for signature validation
        raw_body = request.body

        # Parse the JSON payload
        try:
            payload = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON payload'},
                status=400
            )

        # Get signature header if present
        signature_header = request.META.get('HTTP_X_HUB_SIGNATURE_256') or \
                          request.META.get('HTTP_X_HUB_SIGNATURE')

        # Validate the signature if secret is configured
        webhook_secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', None)
        if webhook_secret and signature_header:
            # Validate the signature
            if not _validate_github_signature(raw_body, signature_header):
                return JsonResponse(
                    {'error': 'Invalid signature'},
                    status=403
                )
        elif webhook_secret and not signature_header:
            # Secret is configured but no signature provided
            return JsonResponse(
                {'error': 'Missing signature header'},
                status=401
            )

        # For non-empty payloads, validate the structure
        if payload and not _validate_payload(payload):
            return JsonResponse(
                {'error': 'Invalid webhook payload format'},
                status=400
            )

        # If we have a valid payload, store it
        if payload:
            # Determine event type from headers or payload
            event_type = request.META.get('HTTP_X_GITHUB_EVENT', 'unknown')
            if not event_type or event_type == 'unknown':
                # Try to infer from payload
                if 'pull_request' in payload:
                    event_type = 'pull_request'
                elif 'issue' in payload:
                    event_type = 'issues'
                elif 'ref' in payload:
                    event_type = 'push'
                else:
                    event_type = 'unknown'

            # Store the webhook event in the database
            webhook = GitHubWebhook.objects.create(
                event_type=event_type,
                payload=payload,
                signature=signature_header,
                processed=True
            )

        return JsonResponse(
            {
                'success': True,
                'message': 'Webhook received and processed'
            },
            status=200
        )

    except Exception as e:
        return JsonResponse(
            {'error': f'Internal server error: {str(e)}'},
            status=500
        )
