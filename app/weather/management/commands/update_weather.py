"""Management command to update weather data for all cities."""
from django.core.management.base import BaseCommand

from weather.models import City, WeatherAlert, WeatherForecast, WeatherRecord
from weather.weather_service import (
    generate_alert,
    generate_current_weather,
    generate_forecast,
)


class Command(BaseCommand):
    """Update weather data for all cities."""

    help = 'Fetch and update weather data for all cities'

    def add_arguments(self, parser) -> None:
        """Add command arguments."""
        parser.add_argument(
            '--city',
            type=str,
            help='Update weather for a specific city by name',
        )

    def handle(self, *args, **options) -> None:
        """Execute the command."""
        city_name = options.get('city')

        if city_name:
            cities = City.objects.filter(name__icontains=city_name)
            if not cities.exists():
                self.stdout.write(self.style.ERROR(f'City "{city_name}" not found'))
                return
        else:
            cities = City.objects.all()

        if not cities.exists():
            self.stdout.write(self.style.WARNING('No cities found in database'))
            return

        self.stdout.write(f'Updating weather data for {cities.count()} cities...')

        for city in cities:
            self.stdout.write(f'Processing {city.name}, {city.country}...')

            # Generate and save current weather
            weather_data = generate_current_weather(city)
            record = WeatherRecord.objects.create(
                city=city,
                **weather_data
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'  Created weather record: {record.temperature}°C, {record.weather_condition}'
                )
            )

            # Generate and save forecasts
            forecast_data = generate_forecast(city, days=7)
            for forecast_dict in forecast_data:
                forecast, created = WeatherForecast.objects.update_or_create(
                    city=city,
                    forecast_date=forecast_dict['forecast_date'],
                    defaults=forecast_dict
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(
                    f'  {action} forecast for {forecast.forecast_date}: '
                    f'{forecast.temperature_min}°C - {forecast.temperature_max}°C'
                )

            # Generate and save alerts if applicable
            alert_data = generate_alert(city)
            if alert_data:
                alert = WeatherAlert.objects.create(
                    city=city,
                    **alert_data
                )
                self.stdout.write(
                    self.style.WARNING(
                        f'  Created alert: {alert.title} ({alert.severity})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully updated weather data for {cities.count()} cities'
            )
        )
