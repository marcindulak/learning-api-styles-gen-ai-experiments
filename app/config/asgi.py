import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.postgres")

# get_asgi_application() must run (and complete Django's app registry setup)
# before importing anything that transitively imports app code, e.g. the
# websocket routing below.
http_application = get_asgi_application()

from weather.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": http_application,
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
