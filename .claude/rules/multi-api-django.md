# Multi-API Django Integration

Single Django project exposes identical data through REST, GraphQL, WebSocket, Atom feeds, and GitHub webhooks using minimal code duplication.

## The Pattern

**Shared Domain Models (app/weather/models.py):**
```python
class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)
    # Single source of truth for all APIs
```

**REST API (app/weather/views.py) — DRF ViewSets:**
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
```

**GraphQL API (app/weather/schema.py) — strawberry-django:**
```python
import strawberry
import strawberry_django

@strawberry_django.type(City)
class CityType:
    uuid: strawberry.auto
    name: strawberry.auto
    country: strawberry.auto

@strawberry.type
class Query:
    @strawberry_django.field
    def cities(self, info: Info) -> list[CityType]:
        return City.objects.all()
```

**WebSocket API (app/weather/consumers.py):**
```python
from channels.generic.websocket import AsyncWebsocketConsumer

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('weather_alerts', self.channel_name)
        await self.accept()
```

**Atom Feeds (app/weather/feeds.py) — Django Syndication:**
```python
from django.contrib.syndication.views import Feed

class ForecastFeed(Feed):
    title = "Weather Forecasts"
    link = "/api/feeds/forecasts/"

    def items(self):
        return Forecast.objects.all().order_by('-created_at')[:10]
```

**URL Configuration (app/config/urls.py):**
```python
urlpatterns = [
    # REST API
    path('api/', include('weather.urls')),

    # GraphQL
    path('api/graphql/', GraphQLView.as_view(schema=schema)),

    # WebSocket (in ASGI)
    # ws://localhost:8001/ws/alerts/

    # Feeds
    path('api/feeds/forecasts/', ForecastFeed()),
]
```

## Why This Pattern

- **Single Model Definition:** Changes to City automatically reflect in all APIs
- **Minimal Serializer Duplication:** Serializers/GraphQL types auto-map from models
- **Shared Authentication:** Django's permission system works across all API types
- **Efficient Database Queries:** ORM optimizations (select_related, prefetch_related) benefit all APIs

## Common Mistakes

- **Different validation rules per API** — Keep all validation in Django model or shared serializers, not scattered
- **Inconsistent field names** — Use `source=` in serializers to map model → API field consistently
- **Missing auth on WebSocket** — Must validate JWT token at handshake, not after connect
- **Separate serializers per API** — Reuse shared serializers across REST + GraphQL via `strawberry_django`

## Examples

**Good:**

```python
# Model validation applies to all APIs
class Forecast(models.Model):
    forecast_date = models.DateField()

    def clean(self):
        # Shared validation for REST, GraphQL, webhooks
        if (self.forecast_date - date.today()).days > 7:
            raise ValidationError("Forecast limited to 7 days ahead")

# Serializer reused in REST + GraphQL
class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ['uuid', 'forecast_date', 'temperature_high']

# GraphQL uses same model validation
@strawberry_django.type(Forecast)
class ForecastType:
    uuid: strawberry.auto
    forecast_date: strawberry.auto
```

**Bad:**

```python
# ❌ Different validation per API — causes inconsistency
class CityViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        if len(serializer.data['name']) < 3:  # REST-only validation
            raise ValidationError()

# ❌ GraphQL mutation doesn't validate
@strawberry.type
class Mutation:
    @strawberry_django.mutation
    def create_city(self, input: CityInput) -> CityType:
        # No validation — different from REST
        return City.objects.create(**vars(input))
```

## Integration Points

- **REST:** Django REST Framework ViewSets with permission classes
- **GraphQL:** strawberry-django bridges models → GraphQL types, inherits model validation
- **WebSocket:** Django Channels consumers use same authentication middleware
- **Feeds:** Django Syndication framework queries same ORM models
- **Webhooks:** Views receive JSON payload, deserialize with shared serializers, save to models

## Key Files

- `app/weather/models.py` — Source of truth for all schemas
- `app/weather/serializers.py` — Shared REST/GraphQL serializers
- `app/weather/schema.py` — GraphQL type definitions auto-mapped from models
- `app/weather/views.py` — REST API ViewSets with shared serializers
- `app/config/urls.py` — Route URLs to all API handlers
- `app/config/asgi.py` — ASGI router for WebSocket + HTTP protocols
