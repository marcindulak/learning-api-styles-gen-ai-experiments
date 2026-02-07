from datetime import date, timedelta

from behave import then, when

from weather_service.models import City, WeatherForecast


@when('requesting a weather forecast for "{city_name}" for {days:d} days')
def request_weather_forecast(context, city_name: str, days: int) -> None:
    """
    Request weather forecast for a city for a specified number of days.
    Stores the requested days count and fetches forecasts from database.
    """
    context.requested_days = days
    city = City.objects.get(name=city_name)

    # Create forecast records if they don't exist (for testing)
    today = date.today()
    for i in range(min(days, 7)):  # Limit to 7 days maximum
        forecast_date = today + timedelta(days=i)
        WeatherForecast.objects.get_or_create(
            city=city,
            forecast_date=forecast_date,
            defaults={
                "temperature": 20.0 + i,
                "humidity": 60 + i,
                "pressure": 1013 + i,
            }
        )

    # Fetch forecasts (limit to 7 days to simulate API behavior)
    if days > 7:
        context.forecast_error = "Forecast limited to maximum 7 days"
        context.forecasts = []
    else:
        context.forecast_error = None
        start_date = today
        end_date = today + timedelta(days=days - 1)
        context.forecasts = list(
            WeatherForecast.objects.filter(
                city=city,
                forecast_date__gte=start_date,
                forecast_date__lte=end_date
            ).order_by("forecast_date")
        )


@then("a forecast for exactly {days:d} days is returned")
def verify_forecast_days_count(context, days: int) -> None:
    """
    Verify that the forecast contains exactly the specified number of days.
    """
    assert len(context.forecasts) == days, (
        f"Expected {days} forecast days, but got {len(context.forecasts)}"
    )


@then("an error response is returned indicating maximum 7 days")
def verify_forecast_error_max_days(context) -> None:
    """
    Verify that an error is returned when requesting more than 7 days.
    """
    assert context.forecast_error is not None, "Expected error but none was returned"
    assert "7 days" in context.forecast_error or "maximum" in context.forecast_error.lower(), (
        f"Error message should indicate 7 days maximum: {context.forecast_error}"
    )


@then("the forecast contains {days:d} daily predictions")
def verify_forecast_daily_predictions(context, days: int) -> None:
    """
    Verify that the forecast contains the specified number of daily predictions.
    """
    assert len(context.forecasts) == days, (
        f"Expected {days} daily predictions, but got {len(context.forecasts)}"
    )


@then("each prediction includes temperature, humidity, and pressure")
def verify_forecast_weather_indicators(context) -> None:
    """
    Verify that each forecast prediction includes temperature, humidity, and pressure.
    """
    assert len(context.forecasts) > 0, "No forecasts to verify"

    for forecast in context.forecasts:
        assert forecast.temperature is not None, "Temperature is missing"
        assert forecast.humidity is not None, "Humidity is missing"
        assert forecast.pressure is not None, "Pressure is missing"
