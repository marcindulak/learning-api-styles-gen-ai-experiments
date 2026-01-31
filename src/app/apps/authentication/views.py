from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView as BaseTokenVerifyView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class TokenObtainPairView(BaseTokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.

    Expected JSON payload:
    {
        "username": "user@example.com",
        "password": "secret"
    }

    Returns:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class TokenRefreshView(BaseTokenRefreshView):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.

    Expected JSON payload:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Returns:
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class TokenVerifyView(BaseTokenVerifyView):
    """
    Takes a token and indicates if it is valid. This view provides no
    information about a token's fitness for a particular use.

    Expected JSON payload:
    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Returns:
    {} (200 OK if valid, 401 if invalid)
    """
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    Returns the current user information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
