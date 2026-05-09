@status-todo
Feature: FR-001 REST API exposes common weather indicators

  The service exposes common weather indicators (temperature, humidity, wind
  speed, pressure) over a REST API.

  Scenario: Get current weather indicators for an existing city
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/current"
    Then the response status is 200
    And the response Content-Type is "application/json"
    And the response body has a key "temperature" with a numeric value
    And the response body has a key "humidity" with a numeric value
    And the response body has a key "wind_speed" with a numeric value
    And the response body has a key "pressure" with a numeric value

  Scenario: Request current weather for an unknown city
    Given the service is running
    When a client sends GET to "/api/cities/Atlantis/weather/current"
    Then the response status is 404
