@status-active
Feature: 002 User Authentication
  As a service
  I want to authenticate users with JWT tokens
  So that users can securely access the API

  Scenario: Admin user can obtain a JWT access token
    Given a user with username "admin" and password "admin" exists
    When the admin user requests a JWT token
    Then a JWT access token is returned
    And the access token is valid for API requests

  Scenario: Regular user can obtain a JWT access token
    Given a user with username "user" and password "password" exists
    When the regular user requests a JWT token
    Then a JWT access token is returned
    And the access token is valid for API requests

  Scenario: Invalid credentials are rejected
    Given a user with username "admin" and password "admin" exists
    When I request a JWT token with username "admin" and password "wrong"
    Then the request fails with an authentication error

  Scenario: User can use JWT token to access protected endpoints
    Given a user with username "admin" and password "admin" exists
    And the user has obtained a valid JWT access token
    When I make a request to a protected endpoint with the access token
    Then the request is successful

  Scenario: Requests without JWT token are rejected
    Given no JWT token is provided
    When I make a request to a protected endpoint
    Then the request fails with an authentication error
