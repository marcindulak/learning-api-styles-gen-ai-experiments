#!/usr/bin/env python
import os
import sys
import django

# Add app path
sys.path.insert(0, '/app/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from django.test import Client
import json

client = Client(enforce_csrf_checks=False)

query = """
{
    weatherByCity(cityName: "Copenhagen") {
        temperature
        humidity
    }
}
"""

response = client.post(
    '/graphql/',
    data=json.dumps({'query': query}),
    content_type='application/json',
)

print(f"Status: {response.status_code}")
print(f"Content: {response.content[:500]}")
