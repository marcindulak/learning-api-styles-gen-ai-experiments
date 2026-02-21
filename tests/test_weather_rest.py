"""
Unit tests for Weather REST API endpoints.
"""
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import City, WeatherRecord, Forecast

User = get_user_model()


class CityAPITestCase(TestCase):
    """Test City REST API endpoints."""

    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='admin', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user')

        self.city = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

    def test_list_cities_unauthenticated_returns_401(self):
        """Unauthenticated users cannot list cities."""
        response = self.client.get('/api/cities/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_cities_authenticated_succeeds(self):
        """Authenticated users can list cities."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_search_cities_by_name(self):
        """Search cities by name query parameter."""
        City.objects.create(name='Delhi', country='India', region='Asia',
                          timezone='Asia/Kolkata', latitude=28.7041, longitude=77.1025)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cities/?search_name=Tokyo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tokyo')

    def test_create_city_as_admin_succeeds(self):
        """Admin users can create cities."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Shanghai',
            'country': 'China',
            'region': 'Asia',
            'timezone': 'Asia/Shanghai',
            'latitude': 31.2304,
            'longitude': 121.4737
        }
        response = self.client.post('/api/cities/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 2)

    def test_create_city_as_regular_user_fails(self):
        """Regular users cannot create cities."""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Shanghai',
            'country': 'China',
            'region': 'Asia',
            'timezone': 'Asia/Shanghai',
            'latitude': 31.2304,
            'longitude': 121.4737
        }
        response = self.client.post('/api/cities/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WeatherRecordAPITestCase(TestCase):
    """Test WeatherRecord REST API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='admin', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user')

        self.city = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

        # Create weather records for the past 7 days
        base_date = date.today()
        for i in range(7):
            WeatherRecord.objects.create(
                city=self.city,
                recorded_at=base_date - timedelta(days=i),
                temperature=20.0 + i,
                feels_like=19.0 + i,
                humidity=50 + i,
                wind_speed=5.0 + i,
                wind_direction=180,
                pressure=1013 + i,
                precipitation=0.0,
                uv_index=5,
                visibility=10.0,
                cloud_cover=50,
                description='Clear'
            )

    def test_list_weather_records_authenticated_succeeds(self):
        """Authenticated users can list weather records."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/weather-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    def test_filter_weather_records_by_city(self):
        """Filter weather records by city UUID."""
        city2 = City.objects.create(name='Delhi', country='India', region='Asia',
                                   timezone='Asia/Kolkata', latitude=28.7041, longitude=77.1025)
        WeatherRecord.objects.create(
            city=city2,
            recorded_at=date.today(),
            temperature=30.0,
            feels_like=32.0,
            humidity=60,
            wind_speed=3.0,
            wind_direction=90,
            pressure=1010,
            precipitation=0.0,
            uv_index=8,
            visibility=8.0,
            cloud_cover=30,
            description='Sunny'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/weather-records/?city={self.city.uuid}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)
        for record in response.data['results']:
            self.assertEqual(record['city'], str(self.city.uuid))

    def test_filter_weather_records_by_date_range(self):
        """Filter weather records by date range."""
        self.client.force_authenticate(user=self.user)
        date_from = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
        date_to = date.today().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/weather-records/?date_from={date_from}&date_to={date_to}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_create_weather_record_as_admin_succeeds(self):
        """Admin users can create weather records."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'city': str(self.city.uuid),
            'recorded_at': date.today().isoformat(),
            'temperature': 25.0,
            'feels_like': 24.0,
            'humidity': 55,
            'wind_speed': 7.0,
            'wind_direction': 90,
            'pressure': 1015,
            'precipitation': 0.0,
            'uv_index': 6,
            'visibility': 10.0,
            'cloud_cover': 40,
            'description': 'Partly cloudy'
        }
        response = self.client.post('/api/weather-records/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_weather_record_as_regular_user_fails(self):
        """Regular users cannot create weather records."""
        self.client.force_authenticate(user=self.user)
        data = {
            'city': str(self.city.uuid),
            'recorded_at': date.today().isoformat(),
            'temperature': 25.0,
            'feels_like': 24.0,
            'humidity': 55,
            'wind_speed': 7.0,
            'wind_direction': 90,
            'pressure': 1015,
            'precipitation': 0.0,
            'uv_index': 6,
            'visibility': 10.0,
            'cloud_cover': 40,
            'description': 'Partly cloudy'
        }
        response = self.client.post('/api/weather-records/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ForecastAPITestCase(TestCase):
    """Test Forecast REST API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='admin', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user')

        self.city = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

        # Create 7-day forecasts
        for i in range(1, 8):
            Forecast.objects.create(
                city=self.city,
                forecast_date=date.today() + timedelta(days=i),
                temperature_high=25.0 + i,
                temperature_low=15.0 + i,
                humidity=50 + i,
                wind_speed=5.0 + i,
                precipitation_probability=20 + i * 5,
                description='Partly cloudy'
            )

    def test_list_forecasts_authenticated_succeeds(self):
        """Authenticated users can list forecasts."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/forecasts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    def test_filter_forecasts_by_city(self):
        """Filter forecasts by city UUID."""
        city2 = City.objects.create(name='Delhi', country='India', region='Asia',
                                   timezone='Asia/Kolkata', latitude=28.7041, longitude=77.1025)
        Forecast.objects.create(
            city=city2,
            forecast_date=date.today() + timedelta(days=1),
            temperature_high=35.0,
            temperature_low=25.0,
            humidity=60,
            wind_speed=3.0,
            precipitation_probability=10,
            description='Sunny'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/forecasts/?city={self.city.uuid}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    def test_create_forecast_with_invalid_date_fails(self):
        """Creating forecast more than 7 days out fails validation."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'city': str(self.city.uuid),
            'forecast_date': (date.today() + timedelta(days=8)).isoformat(),
            'temperature_high': 30.0,
            'temperature_low': 20.0,
            'humidity': 50,
            'wind_speed': 5.0,
            'precipitation_probability': 20,
            'description': 'Clear'
        }
        response = self.client.post('/api/forecasts/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('forecast_date', response.data)

    def test_create_forecast_within_7_days_succeeds(self):
        """Creating forecast within 7 days succeeds."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'city': str(self.city.uuid),
            'forecast_date': (date.today() + timedelta(days=7)).isoformat(),
            'temperature_high': 28.0,
            'temperature_low': 18.0,
            'humidity': 55,
            'wind_speed': 6.0,
            'precipitation_probability': 25,
            'description': 'Cloudy'
        }
        response = self.client.post('/api/forecasts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_forecast_as_regular_user_fails(self):
        """Regular users cannot create forecasts."""
        self.client.force_authenticate(user=self.user)
        data = {
            'city': str(self.city.uuid),
            'forecast_date': (date.today() + timedelta(days=3)).isoformat(),
            'temperature_high': 28.0,
            'temperature_low': 18.0,
            'humidity': 55,
            'wind_speed': 6.0,
            'precipitation_probability': 25,
            'description': 'Cloudy'
        }
        response = self.client.post('/api/forecasts/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
