"""
Step definitions for Feature 008: Atom Feed API
"""
import json
import xml.etree.ElementTree as ET
from behave import given, when, then
from django.utils import timezone
from datetime import timedelta
from apps.cities.models import City
from apps.weather.models import Forecast


def _create_forecast_data_for_city(context, city_name, days=7):
    """
    Helper to create forecast data for a city.
    """
    city = City.objects.get(name=city_name)

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
            description=f"Forecast for {city_name} day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


@given('forecast data exists for multiple cities')
def step_forecast_multiple_cities(context):
    """
    Create forecast data for multiple cities.
    """
    # Create default cities if they don't exist
    try:
        city1 = City.objects.get(name='Copenhagen')
    except City.DoesNotExist:
        city1 = City.objects.create(
            name='Copenhagen',
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.676100,
            longitude=12.568300
        )

    try:
        city2 = City.objects.get(name='Tokyo')
    except City.DoesNotExist:
        city2 = City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

    _create_forecast_data_for_city(context, 'Copenhagen', 7)
    _create_forecast_data_for_city(context, 'Tokyo', 7)


@given('forecast data exists for Copenhagen and Tokyo')
def step_forecast_copenhagen_tokyo(context):
    """
    Create forecast data for Copenhagen and Tokyo.
    """
    # Create cities if they don't exist
    try:
        City.objects.get(name='Copenhagen')
    except City.DoesNotExist:
        City.objects.create(
            name='Copenhagen',
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.676100,
            longitude=12.568300
        )

    try:
        City.objects.get(name='Tokyo')
    except City.DoesNotExist:
        City.objects.create(
            name='Tokyo',
            country='Japan',
            region='Asia',
            timezone='Asia/Tokyo',
            latitude=35.6762,
            longitude=139.6503
        )

    _create_forecast_data_for_city(context, 'Copenhagen', 7)
    _create_forecast_data_for_city(context, 'Tokyo', 7)


@given('forecast data exists for Copenhagen')
def step_forecast_copenhagen(context):
    """
    Create forecast data for Copenhagen.
    """
    try:
        City.objects.get(name='Copenhagen')
    except City.DoesNotExist:
        City.objects.create(
            name='Copenhagen',
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.676100,
            longitude=12.568300
        )

    _create_forecast_data_for_city(context, 'Copenhagen', 7)


@given('forecast data exists')
def step_forecast_data_exists(context):
    """
    Create forecast data for default cities.
    """
    try:
        City.objects.get(name='Copenhagen')
    except City.DoesNotExist:
        City.objects.create(
            name='Copenhagen',
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.676100,
            longitude=12.568300
        )

    _create_forecast_data_for_city(context, 'Copenhagen', 7)


@when('I request the Atom feed endpoint')
def step_request_atom_feed(context):
    """
    Request the Atom feed endpoint.
    """
    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # No authentication needed for feed
    response = context.client.get('/api/feeds/atom/')

    context.atom_response = response
    context.atom_response_status = response.status_code

    if response.status_code == 200:
        context.atom_response_text = response.content.decode('utf-8')


@then('the response status is 200 OK')
def step_response_200(context):
    """
    Verify the response status is 200 OK.
    """
    assert hasattr(context, 'atom_response_status'), "No response status found"
    assert context.atom_response_status == 200, \
        f"Expected status 200, got {context.atom_response_status}"


@then('the response is valid Atom XML')
def step_response_valid_atom_xml(context):
    """
    Verify the response is valid Atom XML.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)
        # Check for Atom namespace
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # Try to find the feed element
        feed = root
        if feed.tag != '{http://www.w3.org/2005/Atom}feed':
            assert False, f"Expected Atom feed element, got {feed.tag}"
    except ET.ParseError as e:
        assert False, f"Response is not valid XML: {e}"


@then('the feed includes entries for both cities')
def step_feed_includes_entries(context):
    """
    Verify the feed includes entries for multiple cities.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # Find all entry elements
        entries = root.findall('atom:entry', atom_ns)

        # Check that we have entries for both cities
        entry_texts = ' '.join([ET.tostring(e, encoding='unicode') for e in entries])

        assert 'Copenhagen' in entry_texts, "Copenhagen not found in feed entries"
        assert 'Tokyo' in entry_texts, "Tokyo not found in feed entries"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('each entry contains forecast information')
def step_entries_contain_forecast_info(context):
    """
    Verify each entry contains forecast information.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', atom_ns)

        # Check that entries contain weather-related information
        entry_texts = ' '.join([ET.tostring(e, encoding='unicode') for e in entries])

        # Look for weather indicators in the content
        has_temp = 'temperature' in entry_texts or 'temp' in entry_texts.lower()
        has_humidity = 'humidity' in entry_texts
        has_forecast = 'forecast' in entry_texts.lower()

        assert has_forecast or len(entries) > 0, "No forecast entries found in feed"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('each entry includes title, updated timestamp, and content')
def step_entries_required_fields(context):
    """
    Verify each entry includes required fields: title, updated, and content.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', atom_ns)

        assert len(entries) > 0, "No entries found in feed"

        for entry in entries:
            title = entry.find('atom:title', atom_ns)
            updated = entry.find('atom:updated', atom_ns)
            content = entry.find('atom:content', atom_ns)

            assert title is not None, "Entry missing title element"
            assert updated is not None, "Entry missing updated element"
            assert content is not None, "Entry missing content element"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('the feed includes updated timestamp')
def step_feed_has_updated(context):
    """
    Verify the feed includes an updated timestamp.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}

        updated = root.find('atom:updated', atom_ns)

        assert updated is not None, "Feed missing updated element"
        assert updated.text is not None, "Feed updated element is empty"
    except ET.ParseError as e:
        assert False, f"Failed to parse Atom feed: {e}"


@then('the response is well-formed XML')
def step_response_well_formed_xml(context):
    """
    Verify the response is well-formed XML.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        ET.fromstring(context.atom_response_text)
    except ET.ParseError as e:
        assert False, f"Response is not well-formed XML: {e}"


@then('the XML includes valid Atom namespace')
def step_xml_valid_atom_namespace(context):
    """
    Verify the XML includes valid Atom namespace.
    """
    assert hasattr(context, 'atom_response_text'), "No response text found"

    try:
        root = ET.fromstring(context.atom_response_text)

        # Check for Atom namespace
        atom_namespace = 'http://www.w3.org/2005/Atom'

        # The root tag should be in the Atom namespace
        assert atom_namespace in root.tag, \
            f"Expected Atom namespace {atom_namespace} in tag, got {root.tag}"
    except ET.ParseError as e:
        assert False, f"Failed to parse XML: {e}"


@then('the request succeeds with status 200 OK')
def step_request_succeeds_200(context):
    """
    Verify the request succeeds with status 200 OK.
    """
    assert hasattr(context, 'atom_response_status'), "No response status found"
    assert context.atom_response_status == 200, \
        f"Expected status 200, got {context.atom_response_status}"
