import xml.etree.ElementTree as ET
from datetime import date, timedelta

from behave import given, then

from weather.models import City, Forecast

ATOM_NS = "{http://www.w3.org/2005/Atom}"
FORECAST_CONDITIONS = ["Clear", "Cloudy", "Rain", "Sunny", "Windy", "Storm", "Fog"]


def _feed_entries(context):
    return ET.fromstring(context.last_response.content).findall(f"{ATOM_NS}entry")


def _city_forecasts(context):
    return Forecast.objects.filter(city=context.forecast_city)


@given('"{name}" has a 7-day forecast with one entry per day')
def step_given_seven_day_forecast(context, name):
    city = City.objects.get(name=name)
    context.forecast_city = city
    start = date.today()
    Forecast.objects.bulk_create(
        Forecast(
            city=city,
            date=start + timedelta(days=day_offset),
            condition=FORECAST_CONDITIONS[day_offset],
            temp_min=10.0 + day_offset,
            temp_max=20.0 + day_offset,
        )
        for day_offset in range(7)
    )


@then('the response content type is "{content_type}"')
def step_then_content_type(context, content_type):
    assert context.last_response["Content-Type"].startswith(content_type)


@then("the response body is a well-formed Atom document")
def step_then_well_formed_atom(context):
    root = ET.fromstring(context.last_response.content)
    assert root.tag == f"{ATOM_NS}feed"


@then("the feed contains exactly {count:d} entries")
def step_then_feed_entry_count(context, count):
    assert len(_feed_entries(context)) == count


@then("each entry has a title containing that day's forecast date")
def step_then_entries_have_date_titles(context):
    for forecast, entry in zip(_city_forecasts(context), _feed_entries(context)):
        title = entry.find(f"{ATOM_NS}title").text
        assert str(forecast.date) in title


@then("each entry has a summary containing that day's condition and temperature range")
def step_then_entries_have_condition_and_range(context):
    for forecast, entry in zip(_city_forecasts(context), _feed_entries(context)):
        summary = entry.find(f"{ATOM_NS}summary").text
        assert forecast.condition in summary
        assert str(forecast.temp_min) in summary
        assert str(forecast.temp_max) in summary
