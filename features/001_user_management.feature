@status-done
Feature: 001 User Management
  The Weather Forecast Service supports two types of users: admin and regular user.
  Admin users can manage content, while regular users can only view public data.

  Scenario: Admin user can authenticate
    Given the service is running
    When I send a POST request to "/api/jwt/obtain" with credentials "admin" and "admin"
    Then the response status code is 200
    And the response contains an "access" token
    And the response contains a "refresh" token

  Scenario: Regular user can authenticate
    Given the service is running
    And a regular user "testuser" with password "testpass123" exists
    When I send a POST request to "/api/jwt/obtain" with credentials "testuser" and "testpass123"
    Then the response status code is 200
    And the response contains an "access" token
    And the response contains a "refresh" token

  Scenario: Invalid credentials are rejected
    Given the service is running
    When I send a POST request to "/api/jwt/obtain" with credentials "invalid" and "wrong"
    Then the response status code is 401
    And the response does not contain an "access" token
