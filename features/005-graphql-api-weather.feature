@status-done
Feature: 005 GraphQL API Weather Indicators
  As an API consumer
  I want to access weather indicators via GraphQL API
  So that I can query exactly the fields I need

  Scenario: Current weather data is accessible via GraphQL
    Given a city "Copenhagen" exists
    And current weather data exists for Copenhagen
    When I query weather for Copenhagen via GraphQL requesting temperature and humidity
    Then the response includes only requested fields
    And the response status is 200 OK

  Scenario: GraphQL API accepts custom field selection
    Given a city "Copenhagen" exists
    And current weather data exists for Copenhagen
    When I query weather via GraphQL requesting temperature, humidity, and wind_speed
    Then only the requested fields are returned in the response

  Scenario: GraphQL API returns 404-equivalent for non-existent city
    Given no city named "NonExistent" exists
    When I query weather for "NonExistent" via GraphQL
    Then the response contains an error indicating city not found

  Scenario: GraphQL API returns null for missing optional fields
    Given a city "Copenhagen" exists
    And weather data exists without a description field
    When I query weather via GraphQL requesting all fields including description
    Then the description field is null in the response
    And other fields are present

  Scenario: Authenticated users can access GraphQL endpoints
    Given I am authenticated as a regular user
    And a city "Copenhagen" exists with weather data
    When I query weather via GraphQL with authentication
    Then the request succeeds with status 200
