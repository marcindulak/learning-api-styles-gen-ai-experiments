@status-todo
Feature: FR-002 GraphQL API exposes common weather indicators

  The service exposes the same common weather indicators over a GraphQL API at
  "/graphql".

  Scenario: Query current weather via GraphQL for an existing city
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends a GraphQL query "{ currentWeather(city: \"Tokyo\") { temperature humidity windSpeed pressure } }" to "/graphql"
    Then the response status is 200
    And the response body has a key "data.currentWeather.temperature" with a numeric value
    And the response body has a key "data.currentWeather.humidity" with a numeric value
    And the response body has a key "data.currentWeather.windSpeed" with a numeric value
    And the response body has a key "data.currentWeather.pressure" with a numeric value

  Scenario: Query current weather via GraphQL for an unknown city
    Given the service is running
    When a client sends a GraphQL query "{ currentWeather(city: \"Atlantis\") { temperature } }" to "/graphql"
    Then the response status is 200
    And the response body has a key "errors[0].message" with the value "City not found"
