from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/alerts/(?P<city_uuid>[0-9a-fA-F-]+)/$", consumers.AlertConsumer.as_asgi()),
]
