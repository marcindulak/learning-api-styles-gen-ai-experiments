"""REST views for the cities app.

Exposes the ``/api/cities`` collection and the ``/api/cities/{uuid}``
detail endpoint via :class:`rest_framework.viewsets.ModelViewSet`. Read
operations are public; write operations require an authenticated admin
user. The viewset enforces the FR-009 limit of
:data:`cities.models.SUPPORTED_CITY_LIMIT` cities at create time.
"""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from .models import SUPPORTED_CITY_LIMIT, City
from .serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    """List, retrieve, create, update, or delete cities.

    Pagination is provided by the project-wide
    ``DEFAULT_PAGINATION_CLASS`` so list responses include the
    ``count``/``results`` envelope that FR-009 asserts.
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = "uuid"

    def get_permissions(self):
        # Reads are open so the public can list supported cities; writes
        # require an admin (staff or superuser) account.
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        # Reject the request before validation to keep the error message
        # focused on the cap rather than per-field errors that would also
        # fire for an over-limit payload missing optional fields.
        if City.objects.count() >= SUPPORTED_CITY_LIMIT:
            return Response(
                {"detail": f"city limit reached ({SUPPORTED_CITY_LIMIT} cities)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)
