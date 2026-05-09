"""URL routes for the cities app."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import CityViewSet


# trailing_slash=False so REQUIREMENTS.md's curl examples
# (e.g. ``GET /api/cities``) match the routes verbatim.
router = DefaultRouter(trailing_slash=False)
router.register("cities", CityViewSet, basename="city")

urlpatterns = router.urls
