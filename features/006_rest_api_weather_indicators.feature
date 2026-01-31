@status-todo
Feature: 006 - REST API Weather Indicators

  As a user of the Weather Forecast Service
  I want to access common weather indicators via REST API
  So that I can integrate weather data into my applications

  Background:
    Given the Weather Forecast Service is running
    And a city "Tokyo" exists in the system

  Scenario: Get current weather indicators for a city
    Given current weather data exists for city "Tokyo"
    When I request current weather for city "Tokyo"
    Then I receive a response with status code 200
    And the response contains temperature in Celsius
    And the response contains humidity percentage
    And the response contains wind speed in meters per second
    And the response contains atmospheric pressure
    And the response contains weather condition code
    And the response contains weather condition description

  Scenario: Weather data includes measurement timestamp
    Given current weather data exists for city "Tokyo"
    When I request current weather for city "Tokyo"
    Then I receive a response with status code 200
    And the response contains a timestamp field

  Scenario: Weather data is associated with a city
    Given current weather data exists for city "Tokyo"
    When I request current weather for city "Tokyo"
    Then I receive a response with status code 200
    And the response contains the city UUID

  Scenario: Return 404 for weather data of non-existent city
    When I request current weather for non-existent city UUID "00000000-0000-0000-0000-000000000000"
    Then I receive a response with status code 404
