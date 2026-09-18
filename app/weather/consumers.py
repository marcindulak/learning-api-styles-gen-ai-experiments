import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

# Not a standard code (the 4000-4999 range is reserved for application use
# by RFC 6455), chosen to distinguish an auth failure from a generic close.
WS_CLOSE_AUTHENTICATION_FAILED = 4401


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Set before the auth check (and unconditionally) because Channels
        # calls disconnect() -- which reads self.group_name -- whenever the
        # underlying connection closes, even if connect() rejected it here
        # without ever calling accept(); group_discard() on a channel that
        # was never added to the group is a documented no-op, so this is
        # safe to leave set even when this handshake is rejected below.
        city_uuid = self.scope["url_route"]["kwargs"]["city_uuid"]
        self.group_name = f"alerts-{city_uuid}"

        # FR-010: the WebSocket handshake has no Authorization header to
        # carry a bearer token, so, per this project's own "Learning API
        # Styles" ch. 10 (Security) guidance, the JWT travels as a query
        # string parameter on the handshake URL instead.
        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        user = await self._authenticate(token)
        if user is None:
            await self.close(code=WS_CLOSE_AUTHENTICATION_FAILED)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @staticmethod
    async def _authenticate(token):
        # Reuses JWTAuthentication's own get_validated_token/get_user instead
        # of decoding the token by hand, so a WebSocket connection is subject
        # to the same is_active check the REST and GraphQL APIs already get
        # from this class (see schema.py's _authenticated_user).
        #
        # get_validated_token() catches TokenError internally and re-raises
        # InvalidToken (a rest_framework.exceptions.AuthenticationFailed
        # subclass, NOT a TokenError) once every configured token class has
        # failed -- so both exception types must be caught here, or every
        # malformed/expired/tampered token (anything but a missing one)
        # propagates as an unhandled exception instead of a clean rejection.
        if not token:
            return None
        auth = JWTAuthentication()
        try:
            validated_token = auth.get_validated_token(token)
            return await database_sync_to_async(auth.get_user)(validated_token)
        except (TokenError, AuthenticationFailed):
            return None

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def weather_alert(self, event):
        await self.send(text_data=json.dumps(event["alert"]))
