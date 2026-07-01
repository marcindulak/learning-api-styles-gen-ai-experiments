@status-todo
Feature: FR-008 Weather data is limited to the 5 biggest cities in the world
  Automatic weather data collection covers only the 5 biggest cities in the
  world by metropolitan population: Tokyo, Delhi, Shanghai, Sao Paulo, and
  Mexico City. These cities are seeded into the database.

  Scenario: The 5 biggest cities are seeded
    Given the service is running
    And the city seed task has run
    When a client sends a GET request to "/api/cities"
    Then the response status code is 200
    And the response JSON field "results" contains an entry with "name" equal to "Tokyo"
    And the response JSON field "results" contains an entry with "name" equal to "Delhi"
    And the response JSON field "results" contains an entry with "name" equal to "Shanghai"
    And the response JSON field "results" contains an entry with "name" equal to "Sao Paulo"
    And the response JSON field "results" contains an entry with "name" equal to "Mexico City"

  Scenario: Weather data fetch covers only the 5 seeded cities
    Given the service is running
    And the city seed task has run
    And an admin-created city named "Copenhagen" exists
    And the third-party weather API returns valid weather data for any coordinates
    When the weather data fetch task runs for all cities
    Then each of the cities "Tokyo", "Delhi", "Shanghai", "Sao Paulo", "Mexico City" has at least 1 weather record
    And "Copenhagen" has 0 weather records

  Scenario: Running the city seed task twice does not duplicate cities
    Given the service is running
    And the city seed task has run
    When the city seed task runs again
    And a client sends a GET request to "/api/cities?search_name=Tokyo"
    Then the response JSON field "results" contains exactly 1 record
