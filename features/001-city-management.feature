@status-done
Feature: 001 City Management
  As an admin user
  I want to manage cities
  So that the weather service can provide data for specific locations

  Scenario: Admin user can create a city
    Given I am authenticated as an admin user
    When I create a city with name "Copenhagen", country "Denmark", region "Europe", timezone "Europe/Copenhagen", latitude 55.676100, longitude 12.568300
    Then the city is created successfully
    And the city has a UUID identifier

  Scenario: Admin user can retrieve a city by UUID
    Given I am authenticated as an admin user
    And a city "Copenhagen" exists with UUID
    When I retrieve the city by UUID
    Then the city details are returned with all fields intact

  Scenario: Admin user can list cities
    Given I am authenticated as an admin user
    And cities "Copenhagen", "Tokyo", "New York" exist
    When I request a list of all cities
    Then all 3 cities are returned in the list

  Scenario: Admin user can search cities by name
    Given I am authenticated as an admin user
    And cities "Copenhagen", "Barcelona", "Cairo" exist
    When I search for cities with name "Copen"
    Then only "Copenhagen" is returned in the results

  Scenario: Admin user can update a city
    Given I am authenticated as an admin user
    And a city "Copenhagen" exists
    When I update the city timezone to "Europe/Berlin"
    Then the city timezone is updated successfully

  Scenario: Admin user can delete a city
    Given I am authenticated as an admin user
    And a city "Copenhagen" exists
    When I delete the city
    Then the city is removed from the system

  Scenario: Regular user cannot create a city
    Given I am authenticated as a regular user
    When I attempt to create a city with name "Copenhagen"
    Then the request is denied with a permission error

  Scenario: Regular user cannot delete a city
    Given I am authenticated as a regular user
    And a city "Copenhagen" exists
    When I attempt to delete the city
    Then the request is denied with a permission error
