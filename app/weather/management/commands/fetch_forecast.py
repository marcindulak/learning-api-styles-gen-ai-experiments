"""Fetch forecast data from the third-party weather API."""
from django.core.management.base import BaseCommand, CommandError

from weather.fetch import WeatherFetchError, fetch_forecast
from weather.models import City


class Command(BaseCommand):
    help = "Fetch the daily forecast for a city from the third-party weather API"

    def add_arguments(self, parser):
        parser.add_argument("city", help="Name of the city to fetch the forecast for")

    def handle(self, *args, **options):
        name = options["city"]
        try:
            city = City.objects.get(name=name)
        except City.DoesNotExist:
            raise CommandError(f'Unknown city "{name}"')
        try:
            records = fetch_forecast(city)
        except WeatherFetchError as error:
            raise CommandError(
                f'Failed to fetch forecast data for "{name}": {error}'
            )
        self.stdout.write(
            self.style.SUCCESS(f"Stored {len(records)} forecast records for {name}")
        )
