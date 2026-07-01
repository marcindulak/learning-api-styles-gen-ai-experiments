@status-todo
Feature: FR-006 Service has a content management system for admin user
  The service provides a content management system (the Django admin site)
  where the admin user can manage cities, weather records, forecasts, and
  alerts. Non-admin users cannot access the CMS.

  Scenario: Admin user can log in to the CMS
    Given the service is running
    And an admin user "admin" with password "admin" exists
    When the admin user logs in to "/admin/" with username "admin" and password "admin"
    Then the response status code is 200
    And the response body contains "Site administration"

  Scenario: CMS lists the weather domain models for management
    Given the service is running
    And an admin user "admin" with password "admin" exists
    When the admin user logs in to "/admin/" with username "admin" and password "admin"
    Then the CMS index page lists a section for "Cities"
    And the CMS index page lists a section for "Weather records"
    And the CMS index page lists a section for "Forecasts"
    And the CMS index page lists a section for "Alerts"

  Scenario: Admin user can create a city through the CMS
    Given the service is running
    And an admin user "admin" with password "admin" exists
    And the admin user is logged in to the CMS
    When the admin user submits the CMS add-city form with name "Delhi", country "India", region "Asia", timezone "Asia/Kolkata", latitude 28.7041 and longitude 77.1025
    Then a city named "Delhi" exists in the database

  Scenario: Regular user cannot access the CMS
    Given the service is running
    And a regular user "user" with password "user" exists
    When the regular user attempts to log in to "/admin/" with username "user" and password "user"
    Then the CMS login is rejected with an authentication error message
