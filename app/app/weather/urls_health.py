from django.urls import path
from django.http import JsonResponse
from django.views import View


class HealthView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", HealthView.as_view(), name="health"),
]
