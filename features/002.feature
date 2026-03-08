@status-todo
Feature: 002 City Management
  As a system administrator
  I want to manage cities in the system
  So that weather data can be limited to the 5 biggest cities in the world

  Scenario: Admin can create a city
    Given I am authenticated as admin
    When I create a city with the following data:
      | name      | Copenhagen        |
      | country   | Denmark           |
      | region    | Europe            |
      | timezone  | Europe/Copenhagen |
      | latitude  | 55.6761           |
      | longitude | 12.5683           |
    Then the response status code is 201
    And the response contains a field "uuid"
    And the response contains a field "name" with value "Copenhagen"

  Scenario: Regular user cannot create cities
    Given I am authenticated as regular user
    When I create a city with the following data:
      | name    | Tokyo |
      | country | Japan |
    Then the response status code is 403

  Scenario: Unauthenticated users can view cities
    When I send a GET request to "/api/cities"
    Then the response status code is 200
    And the response contains a field "results"

  Scenario: Cities can be searched by name
    Given a city exists with name "London"
    When I send a GET request to "/api/cities?search_name=London"
    Then the response status code is 200
    And the response contains "London"

  Scenario: Cities can be retrieved by UUID
    Given a city exists with name "Paris" and UUID is stored
    When I send a GET request to "/api/cities/{uuid}"
    Then the response status code is 200
    And the response contains a field "name" with value "Paris"
