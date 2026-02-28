Feature: JWT Authentication
  As a user of the Weather Forecast Service
  I want to authenticate using JWT tokens
  So that I can access protected resources

  Scenario: Obtain JWT with valid credentials
    When I POST "/api/jwt/obtain" with valid credentials
    Then the response status is 200
    And the response contains "access" and "refresh" tokens

  Scenario: Obtain JWT with invalid credentials
    When I POST "/api/jwt/obtain" with invalid credentials
    Then the response status is 401

  Scenario: Refresh JWT token
    Given I have a valid refresh token
    When I POST "/api/jwt/refresh" with the refresh token
    Then the response status is 200
    And the response contains a new "access" token
