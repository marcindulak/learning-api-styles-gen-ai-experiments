@status-done
Feature: 001 User Management
  The service must support two types of users: admin and regular user
  with object-level permissions to control access to resources

  Scenario: Admin user can access admin interface
    Given the service is running
    And an admin user exists with username "admin" and password "admin"
    When the admin user logs in
    Then the admin user can access the admin interface

  Scenario: Regular user cannot access admin interface
    Given the service is running
    And a regular user exists with username "user" and password "user"
    When the regular user attempts to access the admin interface
    Then the regular user receives an access denied response

  Scenario: Admin user can perform CRUD operations on cities
    Given the service is running
    And an admin user exists with username "admin" and password "admin"
    And the admin user is authenticated
    When the admin user creates a city with name "Copenhagen"
    Then the city "Copenhagen" is stored in the system

  Scenario: Regular user can read but not modify cities
    Given the service is running
    And a regular user exists with username "user" and password "user"
    And the regular user is authenticated
    And a city "Copenhagen" exists
    When the regular user attempts to read city "Copenhagen"
    Then the city details are returned
    When the regular user attempts to delete city "Copenhagen"
    Then the regular user receives a forbidden response
