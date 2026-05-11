@status-done
Feature: FR-008 Weather records contain actual data

  Weather records returned by the service originate from a third-party weather
  data provider and are not synthetic.

  Scenario: Current weather record reports a third-party source
    Given the service is running
    And the third-party weather provider is configured
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/current"
    Then the response status is 200
    And the response body has a key "source.provider" with a non-empty string value
    And the response body has a key "source.provider" with a value not equal to "stub"
    And the response body has a key "observed_at" with an ISO 8601 timestamp string
    And the response body has a key "temperature" with a numeric value

  Scenario: Service surfaces an error when the third-party provider is unavailable
    Given the service is running
    And the third-party weather provider is unreachable
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/current"
    Then the response status is 503
