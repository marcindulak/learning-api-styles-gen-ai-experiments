import json
import re

from behave import given, then, use_step_matcher, when
from django.test import Client

from weather_service.models import City, WeatherRecord


@when('executing GraphQL query')
def step_execute_graphql_query(context):
    """
    Execute a GraphQL query using the multiline text from the scenario.
    """
    client = Client()
    query = context.text
    response = client.post(
        "/api/graphql",
        data=json.dumps({"query": query}),
        content_type="application/json",
    )
    context.response = response
    if response.status_code == 200:
        context.graphql_data = response.json()


@then('the GraphQL response contains city "{city_name}" with country "{country}"')
def step_graphql_response_contains_city_with_country(context, city_name, country):
    """
    Verify that the GraphQL response contains the specified city with the given country.
    """
    assert context.response.status_code == 200
    data = context.graphql_data
    assert "data" in data
    assert "city" in data["data"]
    city = data["data"]["city"]
    assert city is not None, f"City {city_name} not found in response"
    assert city["name"] == city_name
    assert city["country"] == country


@then('the GraphQL response contains city "{city_name}"')
def step_graphql_response_contains_city(context, city_name):
    """
    Verify that the GraphQL response contains the specified city.
    """
    assert context.response.status_code == 200
    data = context.graphql_data
    assert "data" in data
    assert "cities" in data["data"]
    cities = data["data"]["cities"]
    city_names = [city["name"] for city in cities]
    assert city_name in city_names, f"Expected city {city_name} not found in {city_names}"


@given('a weather record exists for "{city_name}" with temperature {temperature:f} celsius')
def step_weather_record_exists_for_city(context, city_name, temperature):
    """
    Create a weather record for the specified city with the given temperature.
    """
    city = City.objects.get(name=city_name)
    WeatherRecord.objects.create(
        city=city,
        temperature=temperature,
        humidity=50,
        pressure=1013,
        wind_speed=10.0,
        precipitation=0.0,
    )


@then('the GraphQL response contains temperature {temperature:f}')
def step_graphql_response_contains_temperature(context, temperature):
    """
    Verify that the GraphQL response contains the specified temperature.
    """
    assert context.response.status_code == 200
    data = context.graphql_data
    assert "data" in data
    assert "weatherData" in data["data"]
    weather_data = data["data"]["weatherData"]
    assert len(weather_data) > 0, "No weather data found in response"
    temperatures = [float(record["temperature"]) for record in weather_data]
    assert temperature in temperatures, f"Expected temperature {temperature} not found in {temperatures}"
