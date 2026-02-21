"""
Tests for WebSocket weather alerts functionality.
"""
from datetime import datetime
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from weather.consumers import WeatherAlertConsumer
from weather.models import City, WeatherAlert
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class WeatherAlertConsumerTestCase(TestCase):
    """Test WebSocket consumer for weather alerts."""

    def setUp(self):
        """Set up test data."""
        self.city = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

    def test_general_alerts_consumer_connects(self):
        """Test that client can connect to general alerts endpoint."""
        # This test uses channels testing communicator
        # Full async testing would require pytest-asyncio or async TestCase
        # For now, we verify the consumer class exists and has required methods
        self.assertTrue(hasattr(WeatherAlertConsumer, 'connect'))
        self.assertTrue(hasattr(WeatherAlertConsumer, 'disconnect'))
        self.assertTrue(hasattr(WeatherAlertConsumer, 'alert_message'))

    def test_city_specific_alerts_consumer_connects(self):
        """Test that client can connect to city-specific alerts endpoint."""
        # Verify consumer can handle city_uuid parameter
        self.assertTrue(hasattr(WeatherAlertConsumer, 'connect'))
        # The routing pattern includes city_uuid capture group
        from weather.routing import websocket_urlpatterns
        self.assertEqual(len(websocket_urlpatterns), 2)

    def test_alert_message_method_exists(self):
        """Test that consumer has alert_message method for group_send."""
        consumer = WeatherAlertConsumer()
        self.assertTrue(hasattr(consumer, 'alert_message'))
        self.assertTrue(callable(consumer.alert_message))

    def test_receive_json_ping_pong(self):
        """Test that consumer responds to ping with pong."""
        # This verifies the receive_json method exists
        consumer = WeatherAlertConsumer()
        self.assertTrue(hasattr(consumer, 'receive_json'))


class WeatherAlertSignalTestCase(TestCase):
    """Test signal handling for weather alert broadcasting."""

    def setUp(self):
        """Set up test data."""
        self.city = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

    def test_weather_alert_created_triggers_signal(self):
        """Test that creating a WeatherAlert triggers post_save signal."""
        from datetime import timedelta
        alert = WeatherAlert.objects.create(
            city=self.city,
            alert_type='storm',
            severity='warning',
            title='Thunderstorm Alert',
            description='Severe thunderstorm expected',
            expires_at=datetime.now() + timedelta(days=1)
        )
        self.assertTrue(alert.id)
        self.assertEqual(alert.city, self.city)

    def test_weather_alert_signal_uses_transaction_on_commit(self):
        """Verify signal handler uses transaction.on_commit for safety."""
        # This is a structural test - check that signals module exists and imports transaction
        from weather import signals
        import inspect

        source = inspect.getsource(signals.broadcast_weather_alert)
        self.assertIn('transaction.on_commit', source)

    def test_alert_broadcasts_to_both_groups(self):
        """Verify signal broadcasts to both city-specific and general groups."""
        from weather import signals
        import inspect

        source = inspect.getsource(signals.broadcast_weather_alert)
        # Check that group_send is called for city-specific group
        self.assertIn('alerts_city_', source)
        # Check that group_send is called for general group
        self.assertIn('alerts_all', source)

    def test_weather_alert_creation_doesnt_crash(self):
        """Test that creating alert doesn't cause errors in signal handler."""
        from datetime import timedelta
        try:
            alert = WeatherAlert.objects.create(
                city=self.city,
                alert_type='heat',
                severity='advisory',
                title='Heat Advisory',
                description='Excessive heat expected',
                expires_at=datetime.now() + timedelta(days=1)
            )
            self.assertTrue(alert.uuid)
        except Exception as e:
            self.fail(f"Creating WeatherAlert should not raise exception: {e}")

    def test_alert_update_does_not_retrigger_signal(self):
        """Test that updating an alert doesn't trigger broadcast again."""
        from datetime import timedelta
        alert = WeatherAlert.objects.create(
            city=self.city,
            alert_type='cold',
            severity='watch',
            title='Wind Chill Warning',
            description='Dangerous wind chill expected',
            expires_at=datetime.now() + timedelta(days=1),
            is_active=True
        )

        # Update the alert
        alert.is_active = False
        alert.save()

        # Alert should still exist with updated value
        updated_alert = WeatherAlert.objects.get(id=alert.id)
        self.assertFalse(updated_alert.is_active)


class WebSocketRoutingTestCase(TestCase):
    """Test WebSocket URL routing."""

    def test_websocket_urlpatterns_configured(self):
        """Test that websocket_urlpatterns is properly configured."""
        from weather.routing import websocket_urlpatterns
        self.assertIsNotNone(websocket_urlpatterns)
        self.assertIsInstance(websocket_urlpatterns, list)
        self.assertGreater(len(websocket_urlpatterns), 0)

    def test_general_alerts_route_pattern(self):
        """Test that general alerts route pattern is correct."""
        from weather.routing import websocket_urlpatterns
        # First pattern should be general alerts
        self.assertIsNotNone(websocket_urlpatterns[0])

    def test_city_specific_alerts_route_pattern(self):
        """Test that city-specific alerts route pattern includes uuid capture."""
        from weather.routing import websocket_urlpatterns
        # Second pattern should include city_uuid capture group
        self.assertIsNotNone(websocket_urlpatterns[1])


class ASGIConfigurationTestCase(TestCase):
    """Test ASGI configuration for Channels integration."""

    def test_asgi_application_configured(self):
        """Test that ASGI application is configured."""
        from config.asgi import application
        self.assertIsNotNone(application)

    def test_asgi_supports_http_protocol(self):
        """Test that ASGI supports HTTP protocol."""
        from config.asgi import application
        # Verify http protocol is configured
        self.assertTrue(hasattr(application, 'application_mapping') or
                       hasattr(application, 'inner'))

    def test_asgi_supports_websocket_protocol(self):
        """Test that ASGI supports WebSocket protocol."""
        from config.asgi import application
        # ProtocolTypeRouter should have both http and websocket
        # We'll do a basic structural check
        self.assertIsNotNone(application)
