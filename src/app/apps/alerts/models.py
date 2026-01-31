import uuid
from django.db import models
from apps.cities.models import City


class WeatherAlert(models.Model):
    """
    Model representing a weather alert for a city.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
        ('extreme', 'Extreme'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField(help_text="Alert description")
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', 'timestamp']),
        ]
        verbose_name = 'Weather Alert'
        verbose_name_plural = 'Weather Alerts'

    def __str__(self):
        return f"{self.city.name} - {self.severity}: {self.description[:50]}"

    def to_dict(self):
        """Convert alert to dictionary for WebSocket messages."""
        return {
            'uuid': str(self.uuid),
            'city_uuid': str(self.city.uuid),
            'city_name': self.city.name,
            'severity': self.severity,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
