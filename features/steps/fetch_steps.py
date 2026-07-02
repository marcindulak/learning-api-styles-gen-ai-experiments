"""Steps for the third-party weather API fetch tasks.

A stub HTTP server impersonating the third-party weather API runs
inside the behave process, and settings.WEATHER_API_BASE_URL is pointed
at it. The fetch tasks run in-process via call_command, so records are
created in the behave test database and asserted through the ORM.
"""
import json
import threading
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import parse
from behave import given, register_type, step, then, when
from django.conf import settings
from django.core.management import CommandError, call_command
from django.utils import timezone

from weather.fetch import SOURCE
from weather.models import City, ForecastRecord, WeatherRecord


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)


def coordinate_key(latitude, longitude):
    return (round(float(latitude), 4), round(float(longitude), 4))


class StubWeatherAPIHandler(BaseHTTPRequestHandler):
    """Serves the canned third-party responses configured per scenario."""

    def log_message(self, *args):
        pass

    def do_GET(self):
        config = self.server.config
        if config["status"] != 200:
            self._respond(config["status"], {"reason": "stub failure"})
            return
        query = parse_qs(urlparse(self.path).query)
        try:
            key = coordinate_key(query["latitude"][0], query["longitude"][0])
        except (KeyError, ValueError):
            self._respond(400, {"reason": "missing coordinates"})
            return
        payloads = config["cities"].get(key)
        if payloads is None:
            self._respond(404, {"reason": "no data for these coordinates"})
            return
        body = {}
        if "current" in query and "current" in payloads:
            body["current"] = payloads["current"]
        if "daily" in query and "daily" in payloads:
            body["daily"] = payloads["daily"]
        if not body:
            self._respond(404, {"reason": "requested data not configured"})
            return
        self._respond(200, body)

    def _respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def stub_weather_api(context):
    """Start the stub API (once per scenario) and return its config."""
    if getattr(context, "weather_api", None) is not None:
        return context.weather_api
    server = ThreadingHTTPServer(("127.0.0.1", 0), StubWeatherAPIHandler)
    server.config = {"status": 200, "cities": {}}
    threading.Thread(target=server.serve_forever, daemon=True).start()
    original_base_url = settings.WEATHER_API_BASE_URL
    settings.WEATHER_API_BASE_URL = f"http://127.0.0.1:{server.server_port}"

    def cleanup():
        settings.WEATHER_API_BASE_URL = original_base_url
        server.shutdown()
        server.server_close()

    context.add_cleanup(cleanup)
    context.weather_api = server.config
    return server.config


@given(
    "the third-party weather API returns temperature {temperature:g}, "
    "humidity {humidity:g}, wind_speed {wind_speed:g}, pressure {pressure:g}, "
    'precipitation {precipitation:g} for the coordinates of "{name:Q}"'
)
def step_stub_current_weather(
    context, temperature, humidity, wind_speed, pressure, precipitation, name
):
    config = stub_weather_api(context)
    city = City.objects.get(name=name)
    payloads = config["cities"].setdefault(
        coordinate_key(city.latitude, city.longitude), {}
    )
    payloads["current"] = {
        "time": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "temperature_2m": temperature,
        "relative_humidity_2m": humidity,
        "wind_speed_10m": wind_speed,
        "surface_pressure": pressure,
        "precipitation": precipitation,
    }


@given(
    "the third-party weather API returns a 7-day forecast "
    'for the coordinates of "{name:Q}"'
)
def step_stub_daily_forecast(context, name):
    config = stub_weather_api(context)
    city = City.objects.get(name=name)
    payloads = config["cities"].setdefault(
        coordinate_key(city.latitude, city.longitude), {}
    )
    today = timezone.localdate()
    payloads["daily"] = {
        "time": [(today + timedelta(days=day)).isoformat() for day in range(7)],
        "temperature_2m_min": [15.0 + day for day in range(7)],
        "temperature_2m_max": [25.0 + day for day in range(7)],
    }


@given("the third-party weather API responds with status code {status:d}")
def step_stub_failure_status(context, status):
    config = stub_weather_api(context)
    config["status"] = status


@step('"{name:Q}" has {count:d} weather records')
def step_city_weather_record_count(context, name, count):
    city = City.objects.get(name=name)
    actual = city.weather_records.count()
    assert actual == count, (
        f"expected {count} weather records for {name}, got {actual}"
    )


@when('the weather data fetch task runs for the city "{name:Q}"')
def step_run_weather_fetch(context, name):
    context.fetch_error = None
    try:
        call_command("fetch_weather", name)
    except CommandError as error:
        context.fetch_error = error


@when('the forecast data fetch task runs for the city "{name:Q}"')
def step_run_forecast_fetch(context, name):
    context.fetch_error = None
    try:
        call_command("fetch_forecast", name)
    except CommandError as error:
        context.fetch_error = error


@then(
    'a weather record for "{name:Q}" exists with temperature {temperature:g}, '
    "humidity {humidity:g}, wind_speed {wind_speed:g}, pressure {pressure:g}, "
    "precipitation {precipitation:g}"
)
def step_weather_record_with_values_exists(
    context, name, temperature, humidity, wind_speed, pressure, precipitation
):
    record = WeatherRecord.objects.filter(
        city__name=name,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        pressure=pressure,
        precipitation=precipitation,
    ).first()
    assert record is not None, (
        f"no weather record for {name} with the expected values; "
        f"fetch error: {getattr(context, 'fetch_error', None)}"
    )
    context.weather_record = record


@then(
    'the weather record has the field "source" '
    "identifying the third-party weather API"
)
def step_weather_record_source(context):
    actual = context.weather_record.source
    assert actual == SOURCE, (
        f'expected source "{SOURCE}" identifying the third-party API, '
        f'got "{actual}"'
    )


@then('{count:d} forecast records for "{name:Q}" exist')
def step_forecast_record_count_exists(context, count, name):
    city = City.objects.get(name=name)
    actual = city.forecast_records.count()
    assert actual == count, (
        f"expected {count} forecast records for {name}, got {actual}; "
        f"fetch error: {getattr(context, 'fetch_error', None)}"
    )


@then('each forecast record has non-null "{first:Q}" and "{second:Q}" fields')
def step_forecast_records_non_null_fields(context, first, second):
    records = list(ForecastRecord.objects.all())
    assert records, "no forecast records exist to check fields of"
    for record in records:
        for field in (first, second):
            assert getattr(record, field) is not None, (
                f'forecast record {record} has null "{field}"'
            )


@then('the fetch task reports a failure for the city "{name:Q}"')
def step_fetch_task_reports_failure(context, name):
    assert context.fetch_error is not None, (
        "expected the fetch task to fail, but it succeeded"
    )
    assert name in str(context.fetch_error), (
        f'failure message does not mention "{name}": {context.fetch_error}'
    )
