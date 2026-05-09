@status-done
Feature: FR-009 Weather data limited to the 5 biggest cities

  The service stores weather data only for the 5 biggest cities in the world by
  population. The fixed list is: Tokyo (Japan), Delhi (India), Shanghai
  (China), Sao Paulo (Brazil), Mexico City (Mexico).

  Scenario: List the supported cities
    Given the service is running
    When a client sends GET to "/api/cities"
    Then the response status is 200
    And the response body has a key "count" with the value 5
    And the response body has a key "results" listing exactly the city names "Tokyo", "Delhi", "Shanghai", "Sao Paulo", "Mexico City"

  Scenario: Reject creation of a city beyond the 5 supported cities
    Given the service is running
    And the 5 supported cities are already registered
    And the user is authenticated as admin
    When the admin sends POST to "/api/cities" with a payload for a city named "Copenhagen"
    Then the response status is 400
    And the response body has a key "detail" with a value containing "city limit reached"
