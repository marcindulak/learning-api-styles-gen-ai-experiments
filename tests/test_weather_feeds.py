"""
Unit tests for Weather Atom feeds.
"""
from datetime import date, timedelta
from django.test import TestCase, Client
from weather.models import City, Forecast


class AtomFeedTestCase(TestCase):
    """Test Atom feeds for weather forecasts."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create test cities
        self.tokyo = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

        self.delhi = City.objects.create(
            name='Delhi',
            country='India',
            region='Asia',
            timezone='Asia/Kolkata',
            latitude=28.7041,
            longitude=77.1025
        )

        # Create 7-day forecasts for Tokyo
        for i in range(1, 8):
            Forecast.objects.create(
                city=self.tokyo,
                forecast_date=date.today() + timedelta(days=i),
                temperature_high=20.0 + i,
                temperature_low=10.0 + i,
                humidity=50 + i,
                wind_speed=5.0 + i,
                precipitation_probability=10 + i * 5,
                description='Partly cloudy'
            )

        # Create 3-day forecasts for Delhi
        for i in range(1, 4):
            Forecast.objects.create(
                city=self.delhi,
                forecast_date=date.today() + timedelta(days=i),
                temperature_high=30.0 + i,
                temperature_low=20.0 + i,
                humidity=60 + i,
                wind_speed=3.0 + i,
                precipitation_probability=5 + i * 2,
                description='Sunny'
            )

    def test_all_city_forecast_feed_accessible(self):
        """All city forecast feed is accessible."""
        response = self.client.get('/api/feeds/forecasts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/atom+xml; charset=utf-8')

    def test_all_city_forecast_feed_contains_all_cities(self):
        """All city forecast feed contains forecasts from all cities."""
        response = self.client.get('/api/feeds/forecasts/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check that both cities appear in the feed
        self.assertIn('Tokyo', content)
        self.assertIn('Delhi', content)

        # Check that feed contains expected number of entries (10 total forecasts)
        # Each entry has an opening and closing <entry> tag
        entry_count = content.count('<entry>')
        self.assertEqual(entry_count, 10)

    def test_all_city_forecast_feed_is_atom_format(self):
        """All city forecast feed is in Atom format."""
        response = self.client.get('/api/feeds/forecasts/')
        content = response.content.decode('utf-8')

        # Verify Atom XML structure
        self.assertIn('<?xml version="1.0" encoding="utf-8"?>', content)
        self.assertIn('<feed', content)
        self.assertIn('xmlns="http://www.w3.org/2005/Atom"', content)
        self.assertIn('<title>Weather Forecasts - All Cities</title>', content)
        self.assertIn('<entry>', content)

    def test_city_forecast_feed_accessible(self):
        """City-specific forecast feed is accessible."""
        response = self.client.get(f'/api/feeds/forecasts/{self.tokyo.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/atom+xml; charset=utf-8')

    def test_city_forecast_feed_contains_only_city_forecasts(self):
        """City-specific feed contains only that city's forecasts."""
        response = self.client.get(f'/api/feeds/forecasts/{self.tokyo.uuid}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check that Tokyo appears in the feed
        self.assertIn('Tokyo', content)
        self.assertIn('Japan', content)

        # Check that Delhi does NOT appear in Tokyo's feed
        self.assertNotIn('Delhi', content)
        self.assertNotIn('India', content)

        # Tokyo has 7 forecasts
        entry_count = content.count('<entry>')
        self.assertEqual(entry_count, 7)

    def test_city_forecast_feed_title_includes_city_name(self):
        """City-specific feed title includes the city name."""
        response = self.client.get(f'/api/feeds/forecasts/{self.tokyo.uuid}/')
        content = response.content.decode('utf-8')
        self.assertIn('<title>Weather Forecasts - Tokyo, Japan</title>', content)

    def test_city_forecast_feed_invalid_uuid_returns_404(self):
        """City-specific feed with invalid UUID returns 404."""
        response = self.client.get('/api/feeds/forecasts/00000000-0000-0000-0000-000000000000/')
        self.assertEqual(response.status_code, 404)

    def test_feed_entries_contain_weather_data(self):
        """Feed entries contain temperature, humidity, and other weather data."""
        response = self.client.get(f'/api/feeds/forecasts/{self.tokyo.uuid}/')
        content = response.content.decode('utf-8')

        # Check for weather data in the feed
        self.assertIn('High:', content)
        self.assertIn('Low:', content)
        self.assertIn('Humidity:', content)
        self.assertIn('Wind:', content)
        self.assertIn('Precipitation probability:', content)

    def test_feed_entries_have_proper_atom_structure(self):
        """Feed entries have proper Atom structure with required elements."""
        response = self.client.get(f'/api/feeds/forecasts/{self.tokyo.uuid}/')
        content = response.content.decode('utf-8')

        # Each entry should have these required Atom elements
        self.assertIn('<title>', content)
        self.assertIn('<link', content)
        self.assertIn('<summary', content)
        self.assertIn('<published>', content)
        self.assertIn('<updated>', content)
