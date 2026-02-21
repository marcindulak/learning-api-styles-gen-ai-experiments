# Feature: City Management
# Test CRUD operations for cities with permission checks

Feature: City Management
  As a user of the Weather Forecast Service
  I want to manage cities (create, read, update, delete)
  So that I can track weather for different locations

  Scenario: Admin creates a new city
    Given I am an admin user
    When I create a city with name "Paris" in "France"
    Then the city is created successfully
    And the city has a UUID

  Scenario: Regular user can read cities
    Given a city "Tokyo" exists in "Japan"
    And I am a regular user
    When I list all cities
    Then I see the city "Tokyo" in the list

  Scenario: Regular user cannot create cities
    Given I am a regular user
    When I try to create a city with name "Berlin" in "Germany"
    Then I get a 403 Forbidden error

  Scenario: Admin can update a city
    Given a city "London" exists in "United Kingdom"
    And I am an admin user
    When I update the city "London" to have timezone "Europe/London"
    Then the city is updated successfully

  Scenario: Regular user cannot update cities
    Given a city "Madrid" exists in "Spain"
    And I am a regular user
    When I try to update the city "Madrid"
    Then I get a 403 Forbidden error

  Scenario: Admin can delete a city
    Given a city "Barcelona" exists in "Spain"
    And I am an admin user
    When I delete the city "Barcelona"
    Then the city is deleted successfully

  Scenario: Search cities by name
    Given cities exist:
      | name      | country |
      | Tokyo     | Japan   |
      | Delhi     | India   |
      | Shanghai  | China   |
    And I am a regular user
    When I search for cities with name "Tokyo"
    Then I get 1 result
    And the result contains "Tokyo"
