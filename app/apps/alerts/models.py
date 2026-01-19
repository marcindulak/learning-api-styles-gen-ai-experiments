from django.db import models
from apps.cities.models import City


class Alert(models.Model):
    """Model for weather alerts."""

    ALERT_TYPE_CHOICES = [
        ('severe_weather', 'Severe Weather'),
        ('heat_wave', 'Heat Wave'),
        ('cold_snap', 'Cold Snap'),
        ('storm', 'Storm'),
        ('flood', 'Flood'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} - {self.city.name} ({self.severity})"
