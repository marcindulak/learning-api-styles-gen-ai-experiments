import hmac
import hashlib
import json
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from .models import WebhookEvent
from .serializers import WebhookEventSerializer


# Default webhook secret for testing/development
GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'test-webhook-secret')


def verify_github_signature(payload_body, signature_header, secret):
    """
    Verify the signature of a GitHub webhook request.
    """
    if not signature_header:
        return False

    # GitHub sends signature as sha256=<hex digest>
    if not signature_header.startswith('sha256='):
        return False

    expected_signature = signature_header[7:]  # Remove 'sha256=' prefix

    # Compute HMAC signature
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(expected_signature, computed_signature)


class GitHubWebhookView(APIView):
    """
    View to handle incoming GitHub webhooks.
    """
    permission_classes = [AllowAny]  # Webhooks are authenticated via signature

    def post(self, request):
        # Get signature from headers
        signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')

        # Get raw body for signature verification
        payload_body = request.body

        # Verify signature
        if not verify_github_signature(payload_body, signature, GITHUB_WEBHOOK_SECRET):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get event type from headers
        event_type = request.META.get('HTTP_X_GITHUB_EVENT', 'other')
        delivery_id = request.META.get('HTTP_X_GITHUB_DELIVERY', '')

        # If no delivery ID, generate one
        if not delivery_id:
            import uuid
            delivery_id = str(uuid.uuid4())

        # Parse payload
        try:
            if isinstance(request.data, dict):
                payload = request.data
            else:
                payload = json.loads(request.body)
        except json.JSONDecodeError:
            payload = {}

        # Map event type to our choices
        valid_event_types = [choice[0] for choice in WebhookEvent.EVENT_TYPES]
        if event_type not in valid_event_types:
            event_type = 'other'

        # Log the webhook event
        webhook_event = WebhookEvent.objects.create(
            event_type=event_type,
            delivery_id=delivery_id,
            payload=payload
        )

        # Return success with custom header
        response = Response(
            {'status': 'received', 'event_id': str(webhook_event.uuid)},
            status=status.HTTP_200_OK
        )
        response['X-GitHub-Hook-Processed'] = 'true'
        return response


class WebhookEventListView(ListAPIView):
    """
    View to list received webhook events.
    """
    queryset = WebhookEvent.objects.all()
    serializer_class = WebhookEventSerializer
    permission_classes = [IsAuthenticated]
