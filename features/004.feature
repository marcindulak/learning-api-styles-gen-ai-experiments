@status-todo
Feature: 004 REST API for Weather Data
  As a weather service user
  I want to access weather data via REST API
  So that I can integrate weather information into applications

  Scenario: Get current weather by city name
    Given current weather data exists for "Copenhagen"
    When I send a GET request to "/api/weather/current/Copenhagen"
    Then the response status code is 200
    And the response contains fields "temperature", "humidity", "pressure"

  Scenario: Get 7-day forecast by city name
    Given forecast data exists for "Tokyo" for the next 7 days
    When I send a GET request to "/api/weather/forecast/Tokyo"
    Then the response status code is 200
    And the response contains forecast entries

  Scenario: Return 404 for non-existent city
    When I send a GET request to "/api/weather/current/NonExistentCity"
    Then the response status code is 404

  Scenario: List all cities with weather data
    Given weather data exists for multiple cities
    When I send a GET request to "/api/cities"
    Then the response status code is 200
    And the response contains a list of cities
