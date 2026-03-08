"""
Step definitions for Atom feed.
"""
import json
import subprocess
from datetime import date, timedelta
from behave import given, then
from weather.models import City, WeatherForecast


@given('forecast data exists for "{city_name}"')
def step_forecast_data_exists_any(context, city_name):
    """Create forecast data for the specified city (default 3 days)."""
    city = City.objects.filter(name=city_name).first()
    if not city:
        city = City.objects.create(
            name=city_name,
            country="Test Country",
            region="Test Region",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0
        )

    for i in range(1, 4):
        WeatherForecast.objects.create(
            city=city,
            forecast_date=date.today() + timedelta(days=i),
            temperature=20.0 + i,
            humidity=60.0 + i,
            pressure=1013.0,
            wind_speed=10.0 + i
        )


@then('the Content-Type is "{content_type}"')
def step_content_type_is(context, content_type):
    """Verify the Content-Type header."""
    curl_command = [
        "curl",
        "--request", "GET",
        "--silent",
        "--output", "/dev/null",
        "--write-out", "%{content_type}",
        f"http://localhost:8000{context.last_endpoint}"
    ]

    result = subprocess.run(
        curl_command,
        capture_output=True,
        text=True
    )
    actual_content_type = result.stdout.strip()
    assert content_type in actual_content_type, \
        f"Expected Content-Type to contain '{content_type}', but got '{actual_content_type}'"


@then('the feed contains {count:d} entries')
def step_feed_contains_entries(context, count):
    """Verify the number of entries in the Atom feed."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')
    assert len(entries) == count, \
        f"Expected {count} entries, found {len(entries)}"


@then('the feed contains a title "{expected_title}"')
def step_feed_contains_title(context, expected_title):
    """Verify the feed title."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(context.response_body, 'xml')
    title = soup.find('title')
    assert title is not None, "No title found in feed"
    actual_title = title.text.strip()
    assert actual_title == expected_title, \
        f"Expected title '{expected_title}', found '{actual_title}'"


@then('the feed contains updated timestamp')
def step_feed_contains_updated(context):
    """Verify the feed contains an updated timestamp."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(context.response_body, 'xml')
    updated = soup.find('updated')
    assert updated is not None, "No updated timestamp found in feed"
    assert len(updated.text.strip()) > 0, "Updated timestamp is empty"
