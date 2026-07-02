@status-done
Feature: FR-010 Service has two users: admin, and regular user
  The service distinguishes an admin user and a regular user with
  object-level permissions: the admin user can create, update and delete
  resources, while the regular user has read-only access. Reading public
  weather data requires no authentication.

  Scenario: Admin user can create a city via the REST API
    Given the service is running
    And an admin user "admin" with password "admin" exists
    And the admin user has obtained a JWT access token from "/api/jwt/obtain"
    When the admin user sends a POST request to "/api/cities" with name "Copenhagen", country "Denmark", region "Europe", timezone "Europe/Copenhagen", latitude 55.6761 and longitude 12.5683
    Then the response status code is 201
    And a city named "Copenhagen" exists in the database

  Scenario: Regular user cannot create a city via the REST API
    Given the service is running
    And a regular user "user" with password "user" exists
    And the regular user has obtained a JWT access token from "/api/jwt/obtain"
    When the regular user sends a POST request to "/api/cities" with name "Copenhagen", country "Denmark", region "Europe", timezone "Europe/Copenhagen", latitude 55.6761 and longitude 12.5683
    Then the response status code is 403
    And no city named "Copenhagen" exists in the database

  Scenario: Regular user can read cities via the REST API
    Given the service is running
    And a regular user "user" with password "user" exists
    And a city named "Tokyo" exists
    And the regular user has obtained a JWT access token from "/api/jwt/obtain"
    When the regular user sends a GET request to "/api/cities?search_name=Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains an entry with "name" equal to "Tokyo"

  Scenario: Unauthenticated client can read cities but cannot create them
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends a GET request to "/api/cities" without authentication
    Then the response status code is 200
    When a client sends a POST request to "/api/cities" with name "Copenhagen" and no authentication
    Then the response status code is 401

  Scenario: Admin user can delete a city via the REST API
    Given the service is running
    And an admin user "admin" with password "admin" exists
    And a city named "Tokyo" exists
    And the admin user has obtained a JWT access token from "/api/jwt/obtain"
    When the admin user sends a DELETE request to "/api/cities/<city_uuid>" for the city "Tokyo"
    Then the response status code is 204
    And no city named "Tokyo" exists in the database
