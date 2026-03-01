Feature: City Management
  As an admin user
  I want to manage cities
  So that I can track weather data for different locations

  Scenario: Create a new city
    Given I am authenticated as an admin
    When I create a city with name "Tokyo" and country "Japan"
    Then the city should be created successfully
    And the city should have a UUID

  Scenario: List all cities
    Given there are cities in the database
    When I request the list of cities
    Then I should receive a paginated list of cities

  Scenario: Search cities by name
    Given there is a city named "Copenhagen"
    When I search for cities with name "Copenhagen"
    Then I should find the city "Copenhagen" in the results

  Scenario: Get city details
    Given there is a city with UUID
    When I request city details by UUID
    Then I should receive the city information

  Scenario: Update city information
    Given I am authenticated as an admin
    And there is a city to update
    When I update the city timezone
    Then the city timezone should be updated

  Scenario: Delete a city
    Given I am authenticated as an admin
    And there is a city to delete
    When I delete the city
    Then the city should be removed from the database
