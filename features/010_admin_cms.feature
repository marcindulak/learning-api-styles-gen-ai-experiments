@status-todo
Feature: 010 Admin Content Management System
  The Weather Forecast Service has a content management system for admin users.
  Admins can manage cities, weather data, alerts, and system configuration through Django admin.

  Scenario: Admin can access Django admin interface
    Given the service is running
    And I am authenticated as admin
    When I navigate to "/admin/"
    Then the response status code is 200
    And the page contains "Django administration"

  Scenario: Regular user cannot access Django admin
    Given the service is running
    And I am authenticated as a regular user
    When I navigate to "/admin/"
    Then the response status code is 302
    And I am redirected to the login page

  Scenario: Admin can view cities in admin panel
    Given the service is running
    And I am authenticated as admin
    And cities "Copenhagen", "Tokyo" exist
    When I navigate to "/admin/core/city/"
    Then the response status code is 200
    And the page lists city "Copenhagen"
    And the page lists city "Tokyo"

  Scenario: Admin can create a city via admin panel
    Given the service is running
    And I am authenticated as admin
    When I navigate to "/admin/core/city/add/"
    And I submit the city form with:
      | name       | Paris            |
      | country    | France           |
      | region     | Europe           |
      | timezone   | Europe/Paris     |
      | latitude   | 48.856600        |
      | longitude  | 2.352200         |
    Then the city "Paris" is created
    And I am redirected to the city list

  Scenario: Admin can view weather alerts in admin panel
    Given the service is running
    And I am authenticated as admin
    And weather alerts exist for "Copenhagen"
    When I navigate to "/admin/core/weatheralert/"
    Then the response status code is 200
    And the page lists alerts for "Copenhagen"
