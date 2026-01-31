"""
GraphQL Views for Weather Forecast Service.
"""
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import json

from .schema import schema


@method_decorator(csrf_exempt, name='dispatch')
class GraphQLView(View):
    """
    GraphQL endpoint view that handles POST requests with GraphQL queries.
    Supports JWT authentication.
    """

    def post(self, request, *args, **kwargs):
        """Handle GraphQL POST requests."""
        # Authenticate the request using JWT
        auth_result = self._authenticate(request)
        if auth_result is not None and not auth_result:
            return JsonResponse(
                {'errors': [{'message': 'Authentication credentials were not provided or are invalid.'}]},
                status=401
            )

        # Parse the request body
        try:
            body = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {'errors': [{'message': 'Invalid JSON in request body'}]},
                status=400
            )

        query = body.get('query', '')
        variables = body.get('variables', {})
        operation_name = body.get('operationName')

        # Execute the GraphQL query
        result = schema.execute(
            query,
            variables=variables,
            operation_name=operation_name,
            context_value=request
        )

        response_data = {}

        if result.errors:
            response_data['errors'] = [{'message': str(e)} for e in result.errors]

        if result.data:
            response_data['data'] = result.data

        return JsonResponse(response_data)

    def _authenticate(self, request):
        """
        Authenticate the request using JWT.
        Returns True if authenticated, False if auth header is present but invalid,
        None if no auth header is present (allowing unauthenticated requests for introspection).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            # No auth header - allow for introspection queries
            return None

        try:
            jwt_auth = JWTAuthentication()
            # Create a simple object with headers for the authenticator
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple:
                request.user, _ = user_auth_tuple
                return True
            return False
        except AuthenticationFailed:
            return False
        except Exception:
            return False
