@status-todo
Feature: FR-011 Admin and regular user with object-level permissions

  The service has two user roles: admin (Django staff/superuser) and regular
  user. Object-level permissions control who can create, modify, or delete
  weather records.

  Scenario: Admin can create a city
    Given the service is running
    And an admin user with username "admin" and password "admin" exists
    When the admin obtains a JWT access token via POST to "/api/jwt/obtain"
    And the admin sends POST to "/api/cities" with a valid city payload using the access token
    Then the response status is 201

  Scenario: Regular user cannot create a city
    Given the service is running
    And a regular user with username "alice" and password "secret" exists
    When "alice" obtains a JWT access token via POST to "/api/jwt/obtain"
    And "alice" sends POST to "/api/cities" with a valid city payload using the access token
    Then the response status is 403

  Scenario: Anonymous client cannot create a city
    Given the service is running
    When an anonymous client sends POST to "/api/cities" with a valid city payload
    Then the response status is 401

  Scenario: Regular user can read cities
    Given the service is running
    And a regular user with username "alice" and password "secret" exists
    And a city named "Tokyo" exists
    When "alice" obtains a JWT access token via POST to "/api/jwt/obtain"
    And "alice" sends GET to "/api/cities" using the access token
    Then the response status is 200
