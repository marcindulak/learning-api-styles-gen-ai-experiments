"""Fetch current weather data from the third-party weather API."""
from django.core.management.base import BaseCommand, CommandError

from weather.fetch import WeatherFetchError, fetch_weather
from weather.models import City


class Command(BaseCommand):
    help = "Fetch the current weather for a city from the third-party weather API"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "city", nargs="?", help="Name of the city to fetch weather for"
        )
        group.add_argument(
            "--all",
            action="store_true",
            help="Fetch weather for all seeded cities",
        )

    def handle(self, *args, **options):
        if options["all"]:
            cities = City.objects.filter(is_seeded=True)
        else:
            name = options["city"]
            try:
                cities = [City.objects.get(name=name)]
            except City.DoesNotExist:
                raise CommandError(f'Unknown city "{name}"')
        for city in cities:
            try:
                record = fetch_weather(city)
            except WeatherFetchError as error:
                raise CommandError(
                    f'Failed to fetch weather data for "{city.name}": {error}'
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Stored weather record for {city.name} "
                    f"observed at {record.observed_at.isoformat()}"
                )
            )
