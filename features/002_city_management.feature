@status-done
Feature: 002 City Management
  The Weather Forecast Service limits weather data to the 5 biggest cities in the world.
  Cities have geographic information including name, country, region, timezone, latitude, and longitude.

  Scenario: Admin can create a city
    Given the service is running
    And I am authenticated as admin
    When I send a POST request to "/api/cities" with city data:
      | name       | Copenhagen       |
      | country    | Denmark          |
      | region     | Europe           |
      | timezone   | Europe/Copenhagen|
      | latitude   | 55.676100        |
      | longitude  | 12.568300        |
    Then the response status code is 201
    And the response contains a "uuid" field
    And the response contains field "name" with value "Copenhagen"

  Scenario: Regular user cannot create a city
    Given the service is running
    And I am authenticated as a regular user
    When I send a POST request to "/api/cities" with city data:
      | name       | Paris            |
      | country    | France           |
      | region     | Europe           |
      | timezone   | Europe/Paris     |
      | latitude   | 48.856600        |
      | longitude  | 2.352200         |
    Then the response status code is 403

  Scenario: Unauthenticated user can view cities
    Given the service is running
    And a city "Copenhagen" exists
    When I send a GET request to "/api/cities"
    Then the response status code is 200
    And the response contains a list with city "Copenhagen"

  Scenario: Search for city by name
    Given the service is running
    And a city "Copenhagen" exists
    When I send a GET request to "/api/cities?search_name=Copenhagen"
    Then the response status code is 200
    And the response contains field "results" with 1 items
    And the first result has field "name" with value "Copenhagen"

  Scenario: Get specific city by UUID
    Given the service is running
    And a city "Copenhagen" with UUID exists
    When I send a GET request to "/api/cities/{uuid}"
    Then the response status code is 200
    And the response contains field "name" with value "Copenhagen"
