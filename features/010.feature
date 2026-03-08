@status-done
Feature: 010 Admin Content Management System
  As a system administrator
  I want to manage weather data through a web interface
  So that I can easily add and update content

  Scenario: Admin can access admin interface
    Given I am authenticated as admin via session
    When I navigate to "/admin/"
    Then the response status code is 200
    And the page contains "Django administration"

  Scenario: Regular user cannot access admin interface
    Given I am authenticated as regular user via session
    When I navigate to "/admin/"
    Then the response status code is 302

  Scenario: Admin can view city list
    Given I am authenticated as admin via session
    And cities exist in the database
    When I navigate to "/admin/weather/city/"
    Then the response status code is 200
    And the page contains a list of cities

  Scenario: Admin can create a city via form
    Given I am authenticated as admin via session
    When I navigate to "/admin/weather/city/add/"
    And I submit the city creation form with:
      | name      | Mumbai |
      | country   | India  |
      | region    | Asia   |
      | timezone  | Asia/Kolkata |
      | latitude  | 19.076 |
      | longitude | 72.8777 |
    Then the response status code is 302
    And a city "Mumbai" exists in the database

  Scenario: Admin can view weather alerts
    Given I am authenticated as admin via session
    And weather alerts exist in the database
    When I navigate to "/admin/weather/weatheralert/"
    Then the response status code is 200
    And the page contains weather alerts
