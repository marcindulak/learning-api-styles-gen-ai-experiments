from django.urls import path
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .schema import schema


class GraphQLView_JWT(GraphQLView):
    """GraphQL view with JWT authentication support"""

    def dispatch(self, request, *args, **kwargs):
        """Add JWT authentication to GraphQL requests"""
        # Try to authenticate using JWT if token is provided
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            jwt_auth = JWTAuthentication()
            try:
                # Validate the token
                user, validated_token = jwt_auth.authenticate_token(token)
                request.user = user
                request.auth = validated_token
            except (InvalidToken, AuthenticationFailed, TypeError):
                # Token is invalid, let GraphQL handle the response
                pass

        return super().dispatch(request, *args, **kwargs)

    def get_context(self, request):
        context = super().get_context(request)
        context['user'] = request.user
        return context


urlpatterns = [
    path('', GraphQLView_JWT.as_view(schema=schema), name='graphql'),
]
