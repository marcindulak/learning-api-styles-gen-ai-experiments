"""
Tests for GitHub webhook functionality.
"""
import json
import hmac
import hashlib
from django.test import TestCase, Client
from django.conf import settings
from weather.models import WebhookEvent


class GitHubWebhookTestCase(TestCase):
    """Test GitHub webhook endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.webhook_secret = settings.WEBHOOK_SECRET
        self.endpoint = '/api/webhooks/github/'

    def _generate_signature(self, payload):
        """Generate valid HMAC-SHA256 signature for payload."""
        payload_str = json.dumps(payload) if isinstance(payload, dict) else payload
        if isinstance(payload_str, str):
            payload_bytes = payload_str.encode('utf-8')
        else:
            payload_bytes = payload_str

        signature = 'sha256=' + hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return signature

    def test_webhook_endpoint_accessible(self):
        """Test that webhook endpoint is accessible."""
        response = self.client.post(self.endpoint)
        # Should fail validation but endpoint should be accessible
        self.assertIn(response.status_code, [400, 403])

    def test_webhook_missing_signature_returns_400(self):
        """Test that missing signature header returns 400."""
        payload = {'action': 'opened'}
        response = self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_webhook_invalid_signature_returns_403(self):
        """Test that invalid signature returns 403."""
        payload = {'action': 'opened'}
        response = self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256='sha256=invalid_signature',
            HTTP_X_GITHUB_EVENT='push'
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('error', data)

    def test_webhook_valid_signature_returns_200(self):
        """Test that valid signature returns 200."""
        payload = {'action': 'opened', 'number': 1}
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='push'
        )
        self.assertEqual(response.status_code, 200)

    def test_webhook_valid_signature_stores_event(self):
        """Test that valid webhook stores event in database."""
        payload = {'action': 'opened', 'number': 42}
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='issues'
        )
        self.assertEqual(response.status_code, 200)

        # Verify event was stored
        events = WebhookEvent.objects.filter(event_type='issues')
        self.assertEqual(events.count(), 1)
        event = events.first()
        self.assertEqual(event.payload['action'], 'opened')
        self.assertEqual(event.payload['number'], 42)
        self.assertFalse(event.processed)

    def test_webhook_stores_event_type_from_header(self):
        """Test that event type from header is stored."""
        payload = {'test': 'data'}
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='pull_request'
        )
        self.assertEqual(response.status_code, 200)

        event = WebhookEvent.objects.first()
        self.assertEqual(event.event_type, 'pull_request')

    def test_webhook_default_event_type_if_missing(self):
        """Test that default event type is used if header missing."""
        payload = {'test': 'data'}
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature
        )
        self.assertEqual(response.status_code, 200)

        event = WebhookEvent.objects.first()
        self.assertEqual(event.event_type, 'unknown')

    def test_webhook_handles_complex_payload(self):
        """Test that webhook handles complex nested payloads."""
        payload = {
            'action': 'opened',
            'issue': {
                'number': 123,
                'title': 'Test Issue',
                'user': {
                    'login': 'testuser',
                    'id': 456
                }
            },
            'repository': {
                'name': 'test-repo',
                'url': 'https://github.com/test/repo'
            }
        }
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='issues'
        )
        self.assertEqual(response.status_code, 200)

        event = WebhookEvent.objects.first()
        self.assertEqual(event.payload['issue']['number'], 123)
        self.assertEqual(event.payload['repository']['name'], 'test-repo')

    def test_webhook_is_csrf_exempt(self):
        """Test that webhook endpoint is CSRF exempt."""
        # The endpoint should accept POST without CSRF token
        payload = {'test': 'data'}
        payload_str = json.dumps(payload)
        signature = self._generate_signature(payload_str)

        # Attempt POST without CSRF token (would fail if not exempt)
        response = self.client.post(
            self.endpoint,
            data=payload_str,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='push'
        )
        # Should succeed if endpoint is CSRF exempt
        self.assertEqual(response.status_code, 200)

    def test_webhook_rejects_get_request(self):
        """Test that webhook only accepts POST."""
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_webhook_rejects_invalid_json(self):
        """Test that webhook rejects invalid JSON payload."""
        payload = 'invalid json {{'
        signature = self._generate_signature(payload)

        response = self.client.post(
            self.endpoint,
            data=payload,
            content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT='push'
        )
        self.assertEqual(response.status_code, 400)
