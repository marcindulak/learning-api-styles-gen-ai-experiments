from datetime import date, datetime, timedelta
from xml.etree import ElementTree

from behave import given, then, when
from django.test import Client

from weather_service.models import City, WeatherForecast


def ensure_atom_tree_parsed(context):
    """
    Ensures the atom_tree is parsed from the response if not already done.
    """
    if not hasattr(context, "atom_tree"):
        if hasattr(context, "response"):
            context.atom_tree = ElementTree.fromstring(context.response.content)
        else:
            raise AssertionError("No response available to parse")


@given('a weather forecast exists for "{city_name}" for the next {days:d} days')
def step_create_forecast_for_days(context, city_name, days):
    city = City.objects.get(name=city_name)
    today = date.today()
    for i in range(1, days + 1):
        forecast_date = today + timedelta(days=i)
        WeatherForecast.objects.get_or_create(
            city=city,
            forecast_date=forecast_date,
            defaults={
                "temperature": 20.0 + i,
                "humidity": 60 + i,
                "pressure": 1013 + i,
            },
        )


@when('requesting Atom feed from "{url}"')
def step_request_atom_feed(context, url):
    context.client = Client()
    context.response = context.client.get(url)


@then("the response is valid Atom XML")
def step_verify_valid_atom_xml(context):
    assert context.response.status_code == 200
    assert "application/atom+xml" in context.response["Content-Type"]

    try:
        context.atom_tree = ElementTree.fromstring(context.response.content)
        assert context.atom_tree.tag.endswith("feed")
    except ElementTree.ParseError as e:
        raise AssertionError(f"Invalid XML: {e}")


@then('the feed contains entries for city "{city_name}"')
def step_verify_feed_contains_city(context, city_name):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries = context.atom_tree.findall("atom:entry", namespace)
    assert len(entries) > 0, "No entries found in feed"

    city_found = False
    for entry in entries:
        title_elem = entry.find("atom:title", namespace)
        if title_elem is not None and city_name in title_elem.text:
            city_found = True
            break

    assert city_found, f"No entries found for city {city_name}"


@then("the Atom feed contains a title element")
def step_verify_feed_has_title(context):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    title = context.atom_tree.find("atom:title", namespace)
    assert title is not None, "Feed missing title element"
    assert title.text, "Title element is empty"


@then("the Atom feed contains updated timestamp")
def step_verify_feed_has_updated(context):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    updated = context.atom_tree.find("atom:updated", namespace)
    assert updated is not None, "Feed missing updated element"
    assert updated.text, "Updated element is empty"


@then("the Atom feed contains author information")
def step_verify_feed_has_author(context):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    author = context.atom_tree.find("atom:author", namespace)
    assert author is not None, "Feed missing author element"
    author_name = author.find("atom:name", namespace)
    assert author_name is not None and author_name.text, "Author missing name"


@then("each entry contains title, link, and summary")
def step_verify_entries_have_required_elements(context):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries = context.atom_tree.findall("atom:entry", namespace)
    assert len(entries) > 0, "No entries found in feed"

    for entry in entries:
        title = entry.find("atom:title", namespace)
        assert title is not None and title.text, "Entry missing title"

        link = entry.find("atom:link", namespace)
        assert link is not None, "Entry missing link"

        summary = entry.find("atom:summary", namespace)
        assert summary is not None and summary.text, "Entry missing summary"


@given('the Atom feed was last updated at "{timestamp}"')
def step_given_feed_last_updated(context, timestamp):
    context.last_updated = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")


@when('a new weather forecast is created for "{city_name}"')
def step_create_new_forecast(context, city_name):
    city = City.objects.get(name=city_name)
    forecast_date = date.today() + timedelta(days=1)
    WeatherForecast.objects.get_or_create(
        city=city,
        forecast_date=forecast_date,
        defaults={
            "temperature": 25.0,
            "humidity": 60,
            "pressure": 1013,
        },
    )


@then('the Atom feed updated timestamp is after "{timestamp}"')
def step_verify_feed_updated_after(context, timestamp):
    ensure_atom_tree_parsed(context)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    updated = context.atom_tree.find("atom:updated", namespace)
    assert updated is not None, "Feed missing updated element"

    updated_dt = datetime.fromisoformat(updated.text.replace("Z", "+00:00"))
    reference_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    assert updated_dt.replace(tzinfo=None) > reference_dt, (
        f"Feed update time {updated_dt} is not after {reference_dt}"
    )
