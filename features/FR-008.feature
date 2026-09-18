@status-todo
Feature: FR-008 - Weather data limited to the 5 biggest cities
  On first startup the service seeds weather data for the 5 biggest
  cities in the world by UN metro-area population: Tokyo, Delhi,
  Shanghai, São Paulo, and Mexico City. The City API itself is not
  restricted to these 5; additional cities can be created by an admin,
  but they receive no automatically seeded weather data.

  Scenario: Service seeds weather data for exactly the 5 biggest cities on first startup
    Given the service starts for the first time with an empty database
    When startup seeding completes
    Then cities named "Tokyo", "Delhi", "Shanghai", "São Paulo", and "Mexico City" exist
    And each of these 5 cities has a current weather record

  Scenario: Adding a 6th city is allowed but receives no seeded weather data
    Given the 5 seeded cities already exist
    When an admin creates a city named "Copenhagen" via "POST /api/cities"
    Then the response status is 201
    And "Copenhagen" has no current weather record until a subsequent provider poll stores one
