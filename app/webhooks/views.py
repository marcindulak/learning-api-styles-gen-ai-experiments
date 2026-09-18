import hashlib
import hmac
import json

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GitHubWebhookEvent


class GitHubWebhookView(APIView):
    def post(self, request):
        signature_header = request.headers.get("X-Hub-Signature-256")
        if not signature_header or not self._signature_is_valid(request.body, signature_header):
            return Response({"errors": ["Invalid or missing signature."]}, status=401)

        GitHubWebhookEvent.objects.create(
            event_type=request.headers.get("X-GitHub-Event", ""),
            delivery_id=request.headers.get("X-GitHub-Delivery", ""),
            payload=json.loads(request.body),
        )
        return Response({"status": "accepted"}, status=200)

    @staticmethod
    def _signature_is_valid(body, signature_header):
        # Constant-time comparison (hmac.compare_digest) is required here to avoid
        # a timing side-channel that would let an attacker recover the digest
        # byte-by-byte from response-time differences.
        digest = hmac.new(settings.WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()
        expected_header = f"sha256={digest}"
        return hmac.compare_digest(expected_header, signature_header)
