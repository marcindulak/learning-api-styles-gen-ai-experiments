@status-todo
Feature: FR-007 Content management system for admin

  The service provides a content management system at "/admin/" that allows an
  admin user to manage weather data and users. Regular users cannot access it.

  Scenario: Admin signs into the CMS
    Given the service is running
    And an admin user with username "admin" and password "admin" exists
    When a browser session sends POST to "/admin/login/" with username "admin" and password "admin"
    And the browser session sends GET to "/admin/"
    Then the response status is 200
    And the response body contains the substring "Site administration"

  Scenario: Regular user cannot sign into the CMS
    Given the service is running
    And a regular user with username "alice" and password "secret" exists
    When a browser session sends POST to "/admin/login/" with username "alice" and password "secret"
    Then the response status is 200
    And the response body contains the substring "staff account"

  Scenario: Anonymous request to the CMS is redirected to login
    Given the service is running
    When a client sends GET to "/admin/" without an active session
    Then the response status is 302
    And the response Location header starts with "/admin/login/"
