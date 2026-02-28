"""Management command to seed the 5 biggest cities."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from weather.models import City

CITIES = [
    {
        "name": "Tokyo",
        "country": "Japan",
        "region": "Asia",
        "timezone": "Asia/Tokyo",
        "latitude": Decimal("35.689500"),
        "longitude": Decimal("139.691700"),
    },
    {
        "name": "Delhi",
        "country": "India",
        "region": "Asia",
        "timezone": "Asia/Kolkata",
        "latitude": Decimal("28.613900"),
        "longitude": Decimal("77.209000"),
    },
    {
        "name": "Shanghai",
        "country": "China",
        "region": "Asia",
        "timezone": "Asia/Shanghai",
        "latitude": Decimal("31.230400"),
        "longitude": Decimal("121.473700"),
    },
    {
        "name": "São Paulo",
        "country": "Brazil",
        "region": "South America",
        "timezone": "America/Sao_Paulo",
        "latitude": Decimal("-23.550500"),
        "longitude": Decimal("-46.633300"),
    },
    {
        "name": "Mexico City",
        "country": "Mexico",
        "region": "North America",
        "timezone": "America/Mexico_City",
        "latitude": Decimal("19.432600"),
        "longitude": Decimal("-99.133200"),
    },
]


class Command(BaseCommand):
    help = "Seed the database with the 5 biggest cities by population."

    def handle(self, *args, **options):
        if City.objects.exists():
            self.stdout.write(self.style.WARNING("Cities already exist, skipping seed."))
            return

        for city_data in CITIES:
            City.objects.create(**city_data)
            self.stdout.write(self.style.SUCCESS(f"Created city: {city_data['name']}"))

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(CITIES)} cities."))
