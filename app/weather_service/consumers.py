"""
WebSocket consumers for weather alerts.
"""
import json
from typing import Set

from channels.generic.websocket import AsyncWebsocketConsumer


class WeatherAlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for weather alerts.
    Handles subscription to city-specific weather alerts.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribed_cities: Set[str] = set()

    async def connect(self):
        """Handle new WebSocket connection."""
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        pass

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Expected message format:
        - Subscribe: {"action": "subscribe", "city": "CityName"}
        - Unsubscribe: {"action": "unsubscribe", "city": "CityName"}
        - Issue Alert (for testing): {"action": "issue_alert", "city": "CityName", "severity": "high"}
        """
        try:
            data = json.loads(text_data)
            action = data.get("action")
            city = data.get("city")

            if action == "subscribe" and city:
                self.subscribed_cities.add(city)
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "subscription_confirmation",
                            "city": city,
                            "status": "subscribed",
                        }
                    )
                )

            elif action == "unsubscribe" and city:
                self.subscribed_cities.discard(city)
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "unsubscription_confirmation",
                            "city": city,
                            "status": "unsubscribed",
                        }
                    )
                )

            elif action == "issue_alert" and city:
                # Testing helper: issue alert to this client if subscribed
                severity = data.get("severity", "medium")
                message = data.get("message", f"Weather alert for {city}")
                await self.send_alert(city, severity, message)

        except (json.JSONDecodeError, KeyError):
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid message format"}
                )
            )

    async def send_alert(self, city: str, severity: str, message: str = ""):
        """
        Send weather alert to client if subscribed to the city.

        Args:
            city: City name for the alert
            severity: Severity level of the alert (e.g., "high", "medium", "low")
            message: Optional alert message
        """
        if city in self.subscribed_cities:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "weather_alert",
                        "city": city,
                        "severity": severity,
                        "message": message,
                    }
                )
            )
