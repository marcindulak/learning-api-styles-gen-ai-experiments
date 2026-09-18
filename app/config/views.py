from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView


class AsyncAPISchemaView(APIView):
    """Serves the hand-authored AsyncAPI document describing this project's
    asynchronous channels (WebSocket alerts, GitHub webhook).

    Unlike /api/schema (drf-spectacular, generated from the synchronous DRF
    views), no library in this project's stack generates an AsyncAPI
    document from Django Channels consumers, so the document is maintained
    by hand at docs/asyncapi.json and served as-is (NFR-005).

    Hand-authoring risks drift from the actual payloads sent by
    weather/signals.py and webhooks/views.py; NFR-005.feature's own
    scenarios only assert the document's structure (valid AsyncAPI, both
    channels present), not payload-schema conformance, so a contract test
    validating real payloads against the embedded schemas was left out of
    this iteration as beyond what the active feature's scenarios require.
    """

    def get(self, request):
        path = Path(settings.BASE_DIR) / "docs" / "asyncapi.json"
        # Served as raw bytes, not parsed+re-serialized: the file already IS
        # the JSON response body, so json.loads()/JsonResponse would only
        # pay a parse/re-encode cost to reproduce the same bytes.
        return HttpResponse(path.read_text(), content_type="application/json")
