import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from weather.models import City, WeatherRecord, Forecast, WeatherAlert


class Command(BaseCommand):
    help = 'Seed database with weather data for 5 major cities'

    # City data: (name, country, region, timezone, lat, lon, temp_min, temp_max)
    CITIES_DATA = [
        ('Tokyo', 'Japan', 'Asia', 'Asia/Tokyo', 35.682839, 139.759455, 5, 35),
        ('Delhi', 'India', 'Asia', 'Asia/Kolkata', 28.704060, 77.102493, 10, 45),
        ('Shanghai', 'China', 'Asia', 'Asia/Shanghai', 31.230391, 121.473701, 2, 38),
        ('São Paulo', 'Brazil', 'South America', 'America/Sao_Paulo', -23.550520, -46.633308, 15, 35),
        ('Mexico City', 'Mexico', 'North America', 'America/Mexico_City', 19.432608, -99.133209, 5, 30),
    ]

    ALERT_TYPES = ['storm', 'heat', 'cold', 'flood', 'wind']
    SEVERITIES = ['advisory', 'watch', 'warning']
    WEATHER_DESCRIPTIONS = [
        'Sunny', 'Partly cloudy', 'Cloudy', 'Overcast',
        'Light rain', 'Rain', 'Heavy rain', 'Thunderstorm',
        'Clear', 'Foggy', 'Misty', 'Drizzle'
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding weather data...')

        # Create cities
        cities = self.create_cities()

        # Create weather records (30 days of historical data)
        self.create_weather_records(cities)

        # Create forecasts (7 days ahead)
        self.create_forecasts(cities)

        # Create sample weather alerts
        self.create_alerts(cities)

        self.stdout.write(self.style.SUCCESS('Successfully seeded weather data!'))

    def create_cities(self):
        """Create the 5 major cities."""
        cities = []
        for name, country, region, timezone, lat, lon, temp_min, temp_max in self.CITIES_DATA:
            city, created = City.objects.get_or_create(
                name=name,
                country=country,
                defaults={
                    'region': region,
                    'timezone': timezone,
                    'latitude': Decimal(str(lat)),
                    'longitude': Decimal(str(lon)),
                }
            )
            if created:
                self.stdout.write(f'Created city: {city}')
            else:
                self.stdout.write(f'City already exists: {city}')
            cities.append((city, temp_min, temp_max))
        return cities

    def create_weather_records(self, cities):
        """Create 30 days of historical weather records for each city."""
        now = datetime.now()
        records_created = 0

        for city, temp_min, temp_max in cities:
            # Check if records already exist
            if city.weather_records.exists():
                self.stdout.write(f'Weather records already exist for {city.name}, skipping...')
                continue

            for day_offset in range(30):
                recorded_at = now - timedelta(days=day_offset)
                temperature = Decimal(str(random.uniform(temp_min, temp_max)))
                feels_like = temperature + Decimal(str(random.uniform(-5, 5)))

                WeatherRecord.objects.create(
                    city=city,
                    recorded_at=recorded_at,
                    temperature=temperature,
                    feels_like=feels_like,
                    humidity=Decimal(str(random.uniform(30, 90))),
                    wind_speed=Decimal(str(random.uniform(0, 50))),
                    wind_direction=Decimal(str(random.uniform(0, 360))),
                    pressure=Decimal(str(random.uniform(980, 1040))),
                    precipitation=Decimal(str(random.uniform(0, 20))),
                    uv_index=Decimal(str(random.uniform(0, 11))),
                    visibility=Decimal(str(random.uniform(1, 20))),
                    cloud_cover=Decimal(str(random.uniform(0, 100))),
                    description=random.choice(self.WEATHER_DESCRIPTIONS)
                )
                records_created += 1

        self.stdout.write(f'Created {records_created} weather records')

    def create_forecasts(self, cities):
        """Create 7-day forecasts for each city."""
        today = date.today()
        forecasts_created = 0

        for city, temp_min, temp_max in cities:
            # Check if forecasts already exist
            if city.forecasts.exists():
                self.stdout.write(f'Forecasts already exist for {city.name}, skipping...')
                continue

            for day_offset in range(1, 8):  # 1-7 days ahead
                forecast_date = today + timedelta(days=day_offset)
                temp_high = Decimal(str(random.uniform(temp_min + 5, temp_max)))
                temp_low = Decimal(str(random.uniform(temp_min, temp_high - 5)))

                Forecast.objects.create(
                    city=city,
                    forecast_date=forecast_date,
                    temperature_high=temp_high,
                    temperature_low=temp_low,
                    humidity=Decimal(str(random.uniform(30, 90))),
                    wind_speed=Decimal(str(random.uniform(0, 50))),
                    precipitation_probability=Decimal(str(random.uniform(0, 100))),
                    description=random.choice(self.WEATHER_DESCRIPTIONS)
                )
                forecasts_created += 1

        self.stdout.write(f'Created {forecasts_created} forecasts')

    def create_alerts(self, cities):
        """Create 1-2 sample active weather alerts."""
        alerts_created = 0

        # Create 1-2 random alerts for random cities
        num_alerts = random.randint(1, 2)
        selected_cities = random.sample([city for city, _, _ in cities], num_alerts)

        for city in selected_cities:
            # Check if active alerts already exist
            if city.alerts.filter(is_active=True).exists():
                self.stdout.write(f'Active alerts already exist for {city.name}, skipping...')
                continue

            alert_type = random.choice(self.ALERT_TYPES)
            severity = random.choice(self.SEVERITIES)
            titles = {
                'storm': 'Severe Thunderstorm Warning',
                'heat': 'Heat Advisory',
                'cold': 'Cold Weather Alert',
                'flood': 'Flood Watch',
                'wind': 'High Wind Warning'
            }

            WeatherAlert.objects.create(
                city=city,
                alert_type=alert_type,
                severity=severity,
                title=titles.get(alert_type, 'Weather Alert'),
                description=f'A {alert_type} {severity} has been issued for {city.name}. Please take necessary precautions.',
                expires_at=datetime.now() + timedelta(days=1),
                is_active=True
            )
            alerts_created += 1

        self.stdout.write(f'Created {alerts_created} weather alerts')
