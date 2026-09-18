from django.core.management.base import BaseCommand

from weather.models import City
from weather.providers import OpenMeteoWeatherProvider
from weather.services import poll_city_weather


class Command(BaseCommand):
    help = "Polls the weather data provider for every city and stores a new weather record."

    def handle(self, *args, **options):
        # One sequential HTTP call and INSERT per city: FR-008 seeds only the
        # 5 biggest cities, so this isn't a hot path, and concurrency/batching
        # isn't worth the added complexity without a measured need.
        provider = OpenMeteoWeatherProvider()
        for city in City.objects.all():
            poll_city_weather(city, provider)
