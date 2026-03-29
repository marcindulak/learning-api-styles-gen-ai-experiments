import logging
from django.core.management.base import BaseCommand
from weather.models import City
from weather.services import fetch_and_store_forecast

logger = logging.getLogger(__name__)

CITIES = [
    {
        "name": "Tokyo",
        "country": "Japan",
        "region": "Asia",
        "timezone": "Asia/Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    {
        "name": "Delhi",
        "country": "India",
        "region": "Asia",
        "timezone": "Asia/Kolkata",
        "latitude": 28.6139,
        "longitude": 77.2090,
    },
    {
        "name": "Shanghai",
        "country": "China",
        "region": "Asia",
        "timezone": "Asia/Shanghai",
        "latitude": 31.2304,
        "longitude": 121.4737,
    },
    {
        "name": "Dhaka",
        "country": "Bangladesh",
        "region": "Asia",
        "timezone": "Asia/Dhaka",
        "latitude": 23.8103,
        "longitude": 90.4125,
    },
    {
        "name": "São Paulo",
        "country": "Brazil",
        "region": "Americas",
        "timezone": "America/Sao_Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
    },
]


class Command(BaseCommand):
    help = "Seed the database with the 5 biggest cities and their 7-day forecasts"

    def handle(self, *args, **options):
        for city_data in CITIES:
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                defaults=city_data,
            )
            action = "Created" if created else "Skipped (already exists)"
            self.stdout.write(f"{action}: {city}")
            if created:
                try:
                    count = fetch_and_store_forecast(city)
                    self.stdout.write(
                        self.style.SUCCESS(f"  Imported {count} forecast days for {city.name}")
                    )
                except Exception:
                    logger.exception("Failed to import forecast for %s", city.name)
                    self.stderr.write(f"  Failed to import forecast for {city.name}")
        self.stdout.write(self.style.SUCCESS("Done."))
