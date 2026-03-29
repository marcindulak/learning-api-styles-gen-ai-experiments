Feature: Cities API
  As a user
  I want to manage cities
  So that I can access weather data

  Scenario: List cities returns empty list initially
    Given I am an unauthenticated user
    When I GET /api/cities
    Then the response status is 200
    And the response contains a results list

  Scenario: Admin can create a city
    Given I am authenticated as admin
    When I POST /api/cities with Tokyo data
    Then the response status is 201
    And the response contains the city name Tokyo

  Scenario: Regular user cannot create a city
    Given I am authenticated as a regular user
    When I POST /api/cities with Delhi data
    Then the response status is 403

  Scenario: GraphQL query returns cities
    Given I am an unauthenticated user
    When I query GraphQL for all cities
    Then the GraphQL response contains a cities list
