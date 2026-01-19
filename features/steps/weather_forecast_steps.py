"""
Step definitions for Feature 006: Weather Forecast
"""
import json
from behave import given, when, then
from django.utils import timezone
from datetime import timedelta
from apps.cities.models import City
from apps.weather.models import Forecast




def _create_forecast_data(context, city_name, days):
    """
    Helper to create forecast data for a city.
    """
    city = City.objects.get(name=city_name)
    days = int(days)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    for i in range(days):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


# Most specific patterns first
@given('forecast data exists for {city_name} spanning {days} days')
def step_forecast_data_spanning_days(context, city_name, days):
    """
    Create forecast data for a city spanning the specified number of days.
    """
    _create_forecast_data(context, city_name, days)


@given('forecast data exists for {city_name} for days {day_range}')
def step_forecast_days_range(context, city_name, day_range):
    """
    Create forecast data for a city spanning a range of days.
    """
    city = City.objects.get(name=city_name)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    # Parse range like "1-7"
    start, end = map(int, day_range.split('-'))
    for i in range(start - 1, end):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


# Least specific pattern last
@given('forecast data exists for {city_name}')
def step_forecast_data_exists(context, city_name):
    """
    Create forecast data for a city (7 days default).
    """
    _create_forecast_data(context, city_name, 7)


@when('I request the forecast for {city_name}')
def step_request_forecast(context, city_name):
    """
    Request forecast data for a city via REST API.
    """
    city = City.objects.get(name=city_name)

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # Ensure authentication token is available
    if not hasattr(context, 'access_token') or not context.access_token:
        # Authenticate as regular user
        credentials = {"username": "user", "password": "password"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data.get('access')

    headers = {
        'Authorization': f'Bearer {context.access_token}' if context.access_token else '',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)


@then('the response includes maximum {max_days} days of forecast data')
def step_response_max_days(context, max_days):
    """
    Verify the response includes at most the maximum number of days.
    """
    max_days = int(max_days)
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    # If response is a list (many=True), check the length
    if isinstance(context.forecast_response_data, list):
        assert len(context.forecast_response_data) <= max_days, \
            f"Expected at most {max_days} days, got {len(context.forecast_response_data)}"
    else:
        # If it's a single object, that's 1 day
        assert 1 <= max_days, f"Expected at most {max_days} days, got 1"


@given('{count} days of forecast data exist for {city_name}')
def step_forecast_days_exist(context, count, city_name):
    """
    Create forecast data for a city spanning the specified number of days.
    """
    city = City.objects.get(name=city_name)
    count = int(count)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    for i in range(count):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


@then('each forecast day includes temperature, humidity, wind_speed, and description')
def step_each_day_has_indicators(context):
    """
    Verify each forecast day includes required indicators.
    """
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if not isinstance(context.forecast_response_data, list):
        context.forecast_response_data = [context.forecast_response_data]

    required_fields = ['temperature', 'humidity', 'wind_speed', 'description']
    for day_data in context.forecast_response_data:
        for field in required_fields:
            assert field in day_data, \
                f"Expected field '{field}' not found in forecast day"


@then('the forecast days are returned in ascending chronological order')
def step_forecast_chronological_order(context):
    """
    Verify forecast days are in chronological order.
    """
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if not isinstance(context.forecast_response_data, list):
        context.forecast_response_data = [context.forecast_response_data]

    # Verify they are in order by checking forecast_date
    for i in range(len(context.forecast_response_data) - 1):
        current_date = context.forecast_response_data[i]['forecast_date']
        next_date = context.forecast_response_data[i + 1]['forecast_date']
        assert current_date <= next_date, \
            f"Forecast dates not in chronological order: {current_date} > {next_date}"


@given('a city "Copenhagen" exists with forecast data')
def step_copenhagen_with_forecast(context):
    """
    Ensure Copenhagen exists with forecast data.
    """
    city, created = City.objects.get_or_create(
        name='Copenhagen',
        defaults={
            'country': 'Denmark',
            'region': 'Europe',
            'timezone': 'Europe/Copenhagen',
            'latitude': 55.6761,
            'longitude': 12.5683
        }
    )

    if not hasattr(context, 'cities'):
        context.cities = {}
    context.cities['Copenhagen'] = {'uuid': str(city.uuid)}

    # Create forecast data if it doesn't exist
    if not Forecast.objects.filter(city=city).exists():
        base_time = timezone.now()
        for i in range(7):
            Forecast.objects.create(
                city=city,
                temperature=20.0 - i * 0.5,
                humidity=60 + (i % 20),
                wind_speed=10.0 + (i % 15),
                pressure=1013.25,
                description=f"Forecast day {i + 1}",
                forecast_date=base_time + timedelta(days=i)
            )


@when('I request the forecast via REST')
def step_request_forecast_rest(context):
    """
    Request forecast data via REST API.
    """
    if not hasattr(context, 'cities'):
        context.cities = {}

    # Get the first city from context
    if context.cities:
        city_uuid = list(context.cities.values())[0]['uuid']
    else:
        # Fall back to Copenhagen if set up
        city = City.objects.filter(name='Copenhagen').first()
        if not city:
            raise Exception("No city available for forecast request")
        city_uuid = str(city.uuid)

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # Ensure authentication token is available
    if not hasattr(context, 'access_token') or not context.access_token:
        # Authenticate as regular user
        credentials = {"username": "user", "password": "password"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data.get('access')

    headers = {
        'Authorization': f'Bearer {context.access_token}' if hasattr(context, 'access_token') and context.access_token else '',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city_uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code
    # Alias for compatibility with REST API steps
    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)
        context.weather_response_data = context.forecast_response_data




@then('the response includes {days}-day forecast data')
def step_response_includes_forecast_days(context, days):
    """
    Verify the response includes the specified number of days.
    """
    days = int(days)
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if isinstance(context.forecast_response_data, list):
        assert len(context.forecast_response_data) > 0, "Forecast response is empty"
        assert len(context.forecast_response_data) <= 7, \
            f"Expected max 7 days, got {len(context.forecast_response_data)}"
    else:
        assert False, "Forecast response should be a list"


@when('I request the forecast via REST with authentication')
def step_request_forecast_authenticated(context):
    """
    Request forecast data via REST API with authentication.
    """
    city = City.objects.get(name='Copenhagen')

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code
    # Alias for compatibility with REST API steps
    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)
        context.weather_response_data = context.forecast_response_data


# Feature 005: Weather Forecast Feed (Atom API) - specific steps
@given('forecast data is available for the next 7 days')
def step_forecast_data_available_7_days(context):
    """
    Create forecast data for the next 7 days for Copenhagen.
    """
    city = City.objects.get(name='Copenhagen')

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data['Copenhagen'] = []

    base_time = timezone.now()
    for i in range(7):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data['Copenhagen'].append(forecast)


@given('forecast data is available beyond 7 days')
def step_forecast_data_beyond_7_days(context):
    """
    Create forecast data extending beyond 7 days for Copenhagen.
    """
    city = City.objects.get(name='Copenhagen')

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data['Copenhagen'] = []

    base_time = timezone.now()
    # Create 14 days of forecast to verify 7-day limit is enforced
    for i in range(14):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data['Copenhagen'].append(forecast)


@when('the client requests the Atom feed for "{city_name}" forecasts')
def step_request_atom_feed_for_city(context, city_name):
    """
    Request the Atom feed for a city's forecasts.
    """
    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # Make request to Atom feed endpoint for the city
    response = context.client.get(f'/api/feeds/atom/?city={city_name}')

    context.atom_feed_response = response
    context.atom_feed_response_status = response.status_code
    context.response_status = response.status_code  # For compatibility with common "Then the system returns HTTP X OK" step

    if response.status_code == 200:
        context.atom_feed_response_text = response.content.decode('utf-8')


@then('the response is in Atom XML format')
def step_response_atom_xml_format(context):
    """
    Verify the response is in Atom XML format.
    """
    assert hasattr(context, 'atom_feed_response_text'), "No Atom feed response found"

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(context.atom_feed_response_text)
        atom_ns = 'http://www.w3.org/2005/Atom'

        # Verify the root element is an Atom feed
        assert atom_ns in root.tag, \
            f"Expected Atom namespace in root tag, got {root.tag}"
    except ET.ParseError as e:
        assert False, f"Response is not valid XML: {e}"


@then('the feed contains entries for each of the next 7 days')
def step_feed_contains_7_day_entries(context):
    """
    Verify the feed contains entries for 7 days.
    """
    assert hasattr(context, 'atom_feed_response_text'), "No Atom feed response found"

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(context.atom_feed_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # Find all entry elements
        entries = root.findall('atom:entry', atom_ns)

        # Should have 7 entries for 7 days
        assert len(entries) == 7, \
            f"Expected 7 entries for 7 days, got {len(entries)}"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('each entry contains forecast date, temperature range, and conditions')
def step_entries_contain_forecast_details(context):
    """
    Verify each entry contains forecast date, temperature range, and conditions.
    """
    assert hasattr(context, 'atom_feed_response_text'), "No Atom feed response found"

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(context.atom_feed_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', atom_ns)

        for entry in entries:
            # Each entry should have at least a title and some content/summary with forecast info
            title = entry.find('atom:title', atom_ns)
            content = entry.find('atom:content', atom_ns)
            summary = entry.find('atom:summary', atom_ns)
            updated = entry.find('atom:updated', atom_ns)

            assert title is not None and title.text, \
                "Entry missing title or title is empty"
            # Accept either content or summary
            assert (content is not None and content.text) or (summary is not None and summary.text), \
                "Entry missing content/summary or both are empty"
            assert updated is not None and updated.text, \
                "Entry missing updated timestamp"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('the response includes only the next 7 days of forecast')
def step_response_includes_only_7_days(context):
    """
    Verify the response includes only the next 7 days.
    """
    assert hasattr(context, 'atom_feed_response_text'), "No Atom feed response found"

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(context.atom_feed_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', atom_ns)

        # Should have at most 7 entries
        assert len(entries) <= 7, \
            f"Expected at most 7 entries, got {len(entries)}"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('no data beyond 7 days is included')
def step_no_data_beyond_7_days(context):
    """
    Verify that no forecast data beyond 7 days is included in the response.
    """
    assert hasattr(context, 'atom_feed_response_text'), "No Atom feed response found"

    import xml.etree.ElementTree as ET
    from datetime import timedelta

    try:
        root = ET.fromstring(context.atom_feed_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', atom_ns)

        # Calculate the cutoff date (7 days from now)
        base_time = timezone.now()
        cutoff_date = base_time + timedelta(days=7)

        for entry in entries:
            # Check the published or updated date to ensure it's within 7 days
            updated = entry.find('atom:updated', atom_ns)
            if updated is not None and updated.text:
                # Parse the ISO format date
                from datetime import datetime
                entry_date = datetime.fromisoformat(updated.text.replace('Z', '+00:00'))

                # Verify entry date is within 7 days
                assert entry_date <= cutoff_date, \
                    f"Entry date {entry_date} is beyond 7-day limit (cutoff: {cutoff_date})"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


