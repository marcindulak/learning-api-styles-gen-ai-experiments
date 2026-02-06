from datetime import datetime

from behave import given, then, when

from weather_service.models import City, WeatherRecord


@when('a weather record is created for "{city_name}" with temperature {temperature:f} celsius')
def step_create_weather_record(context, city_name: str, temperature: float):
    """Create a weather record for the specified city."""
    city = City.objects.get(name=city_name)
    context.weather_record = WeatherRecord.objects.create(
        city=city,
        temperature=temperature,
        humidity=50,
        pressure=1013,
        wind_speed=10.0,
        precipitation=0.0,
    )


@when('a weather record is created for "{city_name}" with the following data')
def step_create_weather_record_with_data(context, city_name: str):
    """Create a weather record with detailed data from the table."""
    city = City.objects.get(name=city_name)
    row = context.table[0]
    context.weather_record = WeatherRecord.objects.create(
        city=city,
        temperature=float(row["temperature"]),
        humidity=int(row["humidity"]),
        pressure=int(row["pressure"]),
        wind_speed=float(row["wind_speed"]),
        precipitation=float(row["precipitation"]),
    )


@when('retrieving historical weather data for "{city_name}"')
def step_retrieve_historical_weather_data(context, city_name: str):
    """Retrieve all weather records for the specified city."""
    city = City.objects.get(name=city_name)
    context.weather_records = list(city.weather_records.all())


@given('the following weather records exist for "{city_name}"')
def step_weather_records_exist(context, city_name: str):
    """Create weather records from table data."""
    city = City.objects.get(name=city_name)
    for row in context.table:
        timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        WeatherRecord.objects.create(
            city=city,
            temperature=float(row["temperature"]),
            humidity=int(row["humidity"]),
            pressure=int(row["pressure"]),
            wind_speed=10.0,
            precipitation=0.0,
        )


@then("the weather record is stored with temperature {temperature:f} celsius")
def step_verify_weather_record_stored(context, temperature: float):
    """Verify the weather record was stored with correct temperature."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        float(context.weather_record.temperature) == temperature
    ), f"Expected temperature {temperature}, got {context.weather_record.temperature}"


@then("{count:d} weather records are returned")
def step_verify_weather_record_count(context, count: int):
    """Verify the number of weather records returned."""
    assert (
        len(context.weather_records) == count
    ), f"Expected {count} weather records, got {len(context.weather_records)}"


@then("the weather record contains temperature {temperature:f} celsius")
def step_verify_temperature(context, temperature: float):
    """Verify the weather record contains the correct temperature."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        float(context.weather_record.temperature) == temperature
    ), f"Expected temperature {temperature}, got {context.weather_record.temperature}"


@then("the weather record contains humidity {humidity:d} percent")
def step_verify_humidity(context, humidity: int):
    """Verify the weather record contains the correct humidity."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        context.weather_record.humidity == humidity
    ), f"Expected humidity {humidity}, got {context.weather_record.humidity}"


@then("the weather record contains pressure {pressure:d} hPa")
def step_verify_pressure(context, pressure: int):
    """Verify the weather record contains the correct pressure."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        context.weather_record.pressure == pressure
    ), f"Expected pressure {pressure}, got {context.weather_record.pressure}"


@then("the weather record contains wind speed {wind_speed:f} km/h")
def step_verify_wind_speed(context, wind_speed: float):
    """Verify the weather record contains the correct wind speed."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        float(context.weather_record.wind_speed) == wind_speed
    ), f"Expected wind speed {wind_speed}, got {context.weather_record.wind_speed}"


@then("the weather record contains precipitation {precipitation:f} mm")
def step_verify_precipitation(context, precipitation: float):
    """Verify the weather record contains the correct precipitation."""
    assert context.weather_record is not None, "Weather record was not created"
    assert (
        float(context.weather_record.precipitation) == precipitation
    ), f"Expected precipitation {precipitation}, got {context.weather_record.precipitation}"
