from django.core.management.base import BaseCommand

from weather.providers import OpenMeteoWeatherProvider
from weather.services import seed_cities


class Command(BaseCommand):
    help = "Seeds the 5 biggest cities in the world with an initial weather record, once."

    def handle(self, *args, **options):
        seed_cities(OpenMeteoWeatherProvider())
