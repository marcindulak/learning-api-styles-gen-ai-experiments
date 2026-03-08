@status-todo
Feature: 005 GraphQL API for Weather Data
  As a weather service developer
  I want to query weather data using GraphQL
  So that I can request only the specific fields needed

  Scenario: Query current weather with selective fields
    Given current weather data exists for "Copenhagen"
    When I execute a GraphQL query for current weather in "Copenhagen" requesting "temperature" and "humidity"
    Then the response status code is 200
    And the GraphQL response contains "temperature" and "humidity" for "Copenhagen"

  Scenario: Query forecast with date limit
    Given forecast data exists for "Tokyo" for the next 7 days
    When I execute a GraphQL query for forecasts in "Tokyo" for the next 3 days
    Then the response status code is 200
    And the GraphQL response contains exactly 3 forecast entries

  Scenario: Query multiple cities in single request
    Given current weather data exists for "Copenhagen" and "Tokyo"
    When I execute a GraphQL query requesting weather for both "Copenhagen" and "Tokyo"
    Then the response status code is 200
    And the GraphQL response contains data for both cities
