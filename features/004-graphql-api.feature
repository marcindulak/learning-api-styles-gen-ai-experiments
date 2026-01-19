@status-done
Feature: 004 GraphQL API for Weather Indicators
  As a client application
  I need to query weather indicators via GraphQL
  So that I can request only the fields I need

  Scenario: Query weather via GraphQL with specific fields
    Given a city "Copenhagen" exists in the system
    And weather data is available for "Copenhagen"
    When the client sends a GraphQL query requesting temperature and humidity for "Copenhagen"
    Then the system returns HTTP 200 OK
    And the response contains only the requested fields (temperature and humidity)
    And the response is in JSON format with GraphQL structure

  Scenario: GraphQL query returns error for invalid field
    Given a GraphQL endpoint is available
    When the client sends a GraphQL query with an invalid field name
    Then the system returns a GraphQL error in the response
    And no data is returned for that field
