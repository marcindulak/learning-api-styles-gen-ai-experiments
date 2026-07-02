"""Fetch current weather data from the third-party weather API."""
from django.core.management.base import BaseCommand, CommandError

from weather.fetch import WeatherFetchError, fetch_weather
from weather.models import City


class Command(BaseCommand):
    help = "Fetch the current weather for a city from the third-party weather API"

    def add_arguments(self, parser):
        parser.add_argument("city", help="Name of the city to fetch weather for")

    def handle(self, *args, **options):
        name = options["city"]
        try:
            city = City.objects.get(name=name)
        except City.DoesNotExist:
            raise CommandError(f'Unknown city "{name}"')
        try:
            record = fetch_weather(city)
        except WeatherFetchError as error:
            raise CommandError(
                f'Failed to fetch weather data for "{name}": {error}'
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Stored weather record for {name} "
                f"observed at {record.observed_at.isoformat()}"
            )
        )
