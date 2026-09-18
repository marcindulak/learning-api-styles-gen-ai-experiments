import logging

from django.contrib.auth.models import User

from .models import City, WeatherRecord
from .providers import WeatherProviderUnavailable

logger = logging.getLogger(__name__)

# FR-008: the 5 biggest cities in the world by UN metro-area population,
# per the ranking decided in ELN ENTRY 001. Coordinates are each city's
# commonly cited center point, used to query the weather data provider.
BIGGEST_CITIES = [
    {"name": "Tokyo", "country": "Japan", "region": "Asia", "timezone": "Asia/Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Delhi", "country": "India", "region": "Asia", "timezone": "Asia/Kolkata", "latitude": 28.7041, "longitude": 77.1025},
    {"name": "Shanghai", "country": "China", "region": "Asia", "timezone": "Asia/Shanghai", "latitude": 31.2304, "longitude": 121.4737},
    {"name": "São Paulo", "country": "Brazil", "region": "South America", "timezone": "America/Sao_Paulo", "latitude": -23.5505, "longitude": -46.6333},
    {"name": "Mexico City", "country": "Mexico", "region": "North America", "timezone": "America/Mexico_City", "latitude": 19.4326, "longitude": -99.1332},
]


def seed_cities(provider):
    """Seeds the 5 biggest cities in the world with an initial weather record.

    A no-op once any city already exists, so this is safe to invoke on
    every container startup without duplicating data after the first run.

    Deliberately a plain function called from a management command, not a
    data migration: this project's compose.yaml runs a single `app`
    container (NFR-003), so the concurrent-startup race a migration's
    row-level locking would avoid does not arise here; a migration would
    also make this function's live provider HTTP call run on every
    `manage.py migrate`, including the one django-behave issues to build
    the ephemeral test database for every test run, defeating the
    FakeWeatherProvider-based testing convention established in FR-007.
    Sequential per-city polling (rather than batching into one provider
    call or parallelizing) is left as-is: this runs once, ever, against 5
    cities, not a hot path (same reasoning as poll_weather.py).
    """
    if City.objects.exists():
        return
    for city_data in BIGGEST_CITIES:
        city = City.objects.create(**city_data)
        poll_city_weather(city, provider)


def seed_admin_user(username, password):
    """Seeds a single admin (is_staff/is_superuser) user, once.

    A no-op once any user already exists, so this is safe to invoke on
    every container startup without resetting an operator's own password
    after the first run. Mirrors seed_cities' idempotency guard above:
    plain management command invoked from startup.sh, not a data
    migration, for the same reasons (single-container topology per
    NFR-003; a migration would also run on every test-database `migrate`
    django-behave issues, seeding a real user in every scenario run).
    """
    if User.objects.exists():
        return
    User.objects.create_superuser(username=username, password=password)
    # REQUIREMENTS.md's own curl walkthrough hardcodes admin/admin, and
    # compose.yaml defaults ADMIN_USERNAME/ADMIN_PASSWORD to exactly that,
    # so seeding it isn't itself a bug to fix here. Flagged by the mandatory
    # /security-review gate as a real risk if an operator ever exposes this
    # service beyond the project's default 127.0.0.1-only port binding
    # without overriding the credentials, so a startup-time warning gives
    # that operator a visible signal instead of a silent default.
    if password == "admin":
        logger.warning("seed_admin_user: seeded superuser %r with the well-known default password", username)


def poll_city_weather(city, provider):
    """Fetches a fresh reading for `city` from `provider` and stores it.

    Leaves any existing weather record for `city` untouched, and logs the
    failure, when `provider` is unavailable.
    """
    try:
        reading = provider.fetch_current(city)
    except WeatherProviderUnavailable:
        logger.warning("weather provider %s unavailable for city %s", provider.name, city.name)
        return None
    return WeatherRecord.objects.create(
        city=city,
        temperature=reading.temperature,
        humidity=reading.humidity,
        wind_speed=reading.wind_speed,
        precipitation_probability=reading.precipitation_probability,
        condition=reading.condition,
        source=provider.name,
    )
