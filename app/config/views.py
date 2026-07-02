from pathlib import Path

from django.http import HttpResponse, JsonResponse

ASYNCAPI_DOCUMENT = Path(__file__).with_name("asyncapi.yaml")


def health(request):
    return JsonResponse({"status": "ok"})


def asyncapi(request):
    return HttpResponse(
        ASYNCAPI_DOCUMENT.read_bytes(), content_type="application/yaml"
    )
