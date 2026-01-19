@status-done
Feature: 002 City Management
  As a service
  I need to store and manage cities
  So that weather data can be associated with specific locations

  Scenario: System is limited to 5 biggest cities
    Given the system has a maximum city limit of 5
    When an admin user tries to add a 6th city
    Then the system rejects the new city with an error message
    And only the 5 cities remain in the system

  Scenario: Create a city with valid data
    Given an admin user is authenticated
    When the admin user creates a city with name "Copenhagen", country "Denmark", region "Europe", timezone "Europe/Copenhagen", latitude 55.6761, longitude 12.5683
    Then the city is stored in the database
    And the city has a unique UUID identifier
    And the system returns HTTP 201 Created

  Scenario: Retrieve a city by UUID
    Given a city "Copenhagen" exists with UUID "550e8400-e29b-41d4-a716-446655440000"
    When the user requests the city by UUID
    Then the system returns the city data including name, country, region, timezone, latitude, and longitude
