import strawberry
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

from .models import WeatherRecord
from .permissions import is_self_or_admin


@strawberry.type
class CurrentWeatherType:
    temperature: float
    humidity: int
    wind_speed: float
    precipitation_probability: int
    condition: str


@strawberry.type
class UserType:
    username: str


def _authenticated_user(info: strawberry.Info) -> User:
    # JWTAuthentication.authenticate() reads request.META directly, so it
    # works against the plain Django HttpRequest strawberry_django's
    # StrawberryDjangoContext exposes, with no DRF Request wrapper needed.
    #
    # Both TokenError and AuthenticationFailed must be caught: authenticate()
    # raises InvalidToken (an AuthenticationFailed subclass, not a TokenError)
    # for any malformed/expired/tampered token, so catching only TokenError
    # would let that case escape as an unhandled exception whose message
    # exposes internal SimpleJWT validation detail to the GraphQL client.
    try:
        result = JWTAuthentication().authenticate(info.context.request)
    except (TokenError, AuthenticationFailed):
        result = None
    if result is None:
        raise Exception("a valid JWT is required")
    user, _ = result
    return user


@strawberry.type
class Query:
    @strawberry.field
    def current_weather(self, city_uuid: str) -> CurrentWeatherType | None:
        return WeatherRecord.objects.filter(city__uuid=city_uuid).latest()

    @strawberry.field
    def user(self, info: strawberry.Info, username: str) -> UserType | None:
        requester = _authenticated_user(info)
        if requester.username == username:
            return requester
        # A nonexistent username and an existing-but-forbidden one raise the
        # same message: distinguishing them would let a caller enumerate
        # which usernames exist via the error text alone.
        denied = Exception(f"not allowed to view the profile of '{username}'")
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            raise denied
        if not is_self_or_admin(requester, target):
            raise denied
        return target


schema = strawberry.Schema(query=Query)
