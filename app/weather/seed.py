"""Seed data for the 5 biggest cities in the world.

Weather data collection is limited to these cities (by metropolitan
population): only seeded cities are covered by the fetch-all task.
"""
from weather.models import City

SEEDED_CITIES = {
    "Tokyo": {
        "country": "Japan",
        "region": "Asia",
        "timezone": "Asia/Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "Delhi": {
        "country": "India",
        "region": "Asia",
        "timezone": "Asia/Kolkata",
        "latitude": 28.7041,
        "longitude": 77.1025,
    },
    "Shanghai": {
        "country": "China",
        "region": "Asia",
        "timezone": "Asia/Shanghai",
        "latitude": 31.2304,
        "longitude": 121.4737,
    },
    "Sao Paulo": {
        "country": "Brazil",
        "region": "South America",
        "timezone": "America/Sao_Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
    },
    "Mexico City": {
        "country": "Mexico",
        "region": "North America",
        "timezone": "America/Mexico_City",
        "latitude": 19.4326,
        "longitude": -99.1332,
    },
}


def seed_cities():
    """Idempotently create the seeded cities; return the created ones."""
    created_cities = []
    for name, attributes in SEEDED_CITIES.items():
        city, created = City.objects.get_or_create(
            name=name, defaults={**attributes, "is_seeded": True}
        )
        if created:
            created_cities.append(city)
    return created_cities
