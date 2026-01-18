from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as BaseTokenRefreshSerializer
from rest_framework_simplejwt.serializers import TokenVerifySerializer as BaseTokenVerifySerializer
from django.contrib.auth.models import User


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    """
    Serializer for obtaining JWT token pair (access + refresh).
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if needed
        token['username'] = user.username
        token['email'] = user.email
        return token


class TokenRefreshSerializer(BaseTokenRefreshSerializer):
    """
    Serializer for refreshing JWT access token.
    """
    pass


class TokenVerifySerializer(BaseTokenVerifySerializer):
    """
    Serializer for verifying JWT token.
    """
    pass


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
        read_only_fields = ('id',)
