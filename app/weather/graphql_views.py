"""
Custom GraphQL views.
"""
from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class PublicGraphQLView(GraphQLView):
    """GraphQL view that allows unauthenticated access."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
