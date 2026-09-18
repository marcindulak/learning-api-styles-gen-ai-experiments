from datetime import date, datetime, time, timedelta

from behave import given, then
from common_steps import _response_body
from django.utils import timezone

from weather.models import City, WeatherRecord


@given('"{name}" has historical weather records for every day from "{start}" to "{end}"')
def step_given_historical_records(context, name, start, end):
    city = City.objects.get(name=name)
    day = date.fromisoformat(start)
    last_day = date.fromisoformat(end)
    records = []
    while day <= last_day:
        records.append(WeatherRecord(
            city=city,
            temperature=20.0,
            humidity=50,
            wind_speed=10.0,
            precipitation_probability=0,
            condition="Clear",
            recorded_at=timezone.make_aware(datetime.combine(day, time.min)),
        ))
        day += timedelta(days=1)
    WeatherRecord.objects.bulk_create(records)


@then("the response body contains {count:d} records")
def step_then_response_contains_records(context, count):
    assert len(_response_body(context)) == count


@then("the records are ordered by date ascending")
def step_then_records_ordered_ascending(context):
    recorded_ats = [record["recorded_at"] for record in _response_body(context)]
    assert recorded_ats == sorted(recorded_ats)
