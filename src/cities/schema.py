"""GraphQL schema for FR-002.

Exposes a single root field ``currentWeather(city: String!)`` returning the
same four placeholder weather indicators as the REST endpoint at
``/api/cities/<name>/weather/current``. The two endpoints share the
``_PLACEHOLDER_READING`` constant so a future FR-008 swap of the placeholder
source replaces both responses in lockstep.

When the named city is not in the seeded set, the resolver raises
``GraphQLError`` so the response carries an ``errors`` array populated
with ``"City not found"``. The HTTP status remains 200, which matches the
GraphQL convention of reporting application-level errors in the body.

graphene-django auto-converts snake_case Python field names to camelCase
in the schema, so ``wind_speed`` is exposed as ``windSpeed`` to clients
without a manual alias.
"""

from __future__ import annotations

import graphene
from graphql import GraphQLError

from cities.models import City
from cities.weather import _PLACEHOLDER_READING


class WeatherType(graphene.ObjectType):
    """Four common weather indicators, mirroring the REST response shape."""

    temperature = graphene.Float()
    humidity = graphene.Float()
    wind_speed = graphene.Float()
    pressure = graphene.Float()


class Query(graphene.ObjectType):
    """Root query type."""

    current_weather = graphene.Field(
        WeatherType,
        city=graphene.String(required=True),
        description="Current weather for a seeded city.",
    )

    def resolve_current_weather(root, info, city: str) -> WeatherType:
        if not City.objects.filter(name=city).exists():
            raise GraphQLError("City not found")
        return WeatherType(
            temperature=_PLACEHOLDER_READING["temperature"],
            humidity=_PLACEHOLDER_READING["humidity"],
            wind_speed=_PLACEHOLDER_READING["wind_speed"],
            pressure=_PLACEHOLDER_READING["pressure"],
        )


schema = graphene.Schema(query=Query)
