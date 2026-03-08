@status-active
Feature: 001 User Management
  As a system administrator
  I want to manage admin and regular users
  So that access to the system can be controlled

  Scenario: Admin user can authenticate
    When I request a JWT access token with username "admin" and password "admin"
    Then the response status code is 200
    And the response contains a field "access"
    And the response contains a field "refresh"

  Scenario: Regular user can authenticate
    Given a user exists with username "user" and password "userpass"
    When I request a JWT access token with username "user" and password "userpass"
    Then the response status code is 200
    And the response contains a field "access"
    And the response contains a field "refresh"

  Scenario: Invalid credentials are rejected
    When I request a JWT access token with username "invalid" and password "wrong"
    Then the response status code is 401
