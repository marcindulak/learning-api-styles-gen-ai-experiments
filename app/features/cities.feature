Feature: City CRUD operations
  As a user of the Weather Forecast Service
  I want to manage cities
  So that I can associate weather data with locations

  Scenario: List cities
    Given the database is seeded with cities
    When I GET "/api/cities"
    Then the response status is 200
    And the response contains a paginated list

  Scenario: Search cities by name
    Given the database is seeded with cities
    When I GET "/api/cities?search_name=Tokyo"
    Then the response status is 200
    And the results contain "Tokyo"

  Scenario: Create a city as admin
    Given I am authenticated as admin
    When I POST "/api/cities" with a valid city payload
    Then the response status is 201
    And the response contains the created city

  Scenario: Create a city as anonymous user
    When I POST "/api/cities" with a valid city payload
    Then the response status is 401

  Scenario: Get city by UUID
    Given the database is seeded with cities
    When I GET a city by its UUID
    Then the response status is 200
    And the response contains the city details

  Scenario: Delete a city as admin
    Given I am authenticated as admin
    And a test city exists
    When I DELETE the test city
    Then the response status is 204
