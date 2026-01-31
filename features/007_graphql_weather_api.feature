@status-done
Feature: 007 - GraphQL Weather API

  As a user of the Weather Forecast Service
  I want to access weather data via GraphQL API
  So that I can query exactly the data I need in a flexible way

  Background:
    Given the Weather Forecast Service is running
    And I have obtained a JWT access token for user "admin"
    And a city "Tokyo" exists in the system

  Scenario: Query all cities via GraphQL
    When I send a GraphQL query for all cities
    Then I receive a response with status code 200
    And the GraphQL response contains a list of cities

  Scenario: Query a specific city by UUID via GraphQL
    When I send a GraphQL query for city "Tokyo" by UUID
    Then I receive a response with status code 200
    And the GraphQL response contains city name "Tokyo"

  Scenario: Query current weather for a city via GraphQL
    Given current weather data exists for city "Tokyo"
    When I send a GraphQL query for current weather of city "Tokyo"
    Then I receive a response with status code 200
    And the GraphQL response contains temperature data
    And the GraphQL response contains humidity data
    And the GraphQL response contains wind speed data

  Scenario: Query weather forecast for a city via GraphQL
    When I send a GraphQL query for weather forecast of city "Tokyo"
    Then I receive a response with status code 200
    And the GraphQL response contains forecast data

  Scenario: Query historical weather data via GraphQL
    Given historical weather data exists for city "Tokyo" on date "2024-01-15"
    When I send a GraphQL query for historical weather of city "Tokyo" on date "2024-01-15"
    Then I receive a response with status code 200
    And the GraphQL response contains historical weather data

  Scenario: GraphQL introspection query returns schema
    When I send a GraphQL introspection query
    Then I receive a response with status code 200
    And the GraphQL response contains schema information
