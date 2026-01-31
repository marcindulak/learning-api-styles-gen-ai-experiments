@status-todo
Feature: 001 - JWT Authentication

  As a user of the Weather Forecast Service
  I want to authenticate using JWT tokens
  So that I can access protected API endpoints

  Background:
    Given the Weather Forecast Service is running
    And an admin user exists with username "admin" and password "admin"

  Scenario: Obtain JWT access token with valid credentials
    When I request a JWT token with username "admin" and password "admin"
    Then I receive a response with status code 200
    And the response contains an "access" token
    And the response contains a "refresh" token

  Scenario: Fail to obtain JWT token with invalid credentials
    When I request a JWT token with username "admin" and password "wrongpassword"
    Then I receive a response with status code 401

  Scenario: Access protected endpoint with valid token
    Given I have obtained a JWT access token for user "admin"
    When I make an authenticated GET request to "/api/cities"
    Then I receive a response with status code 200

  Scenario: Fail to access protected endpoint without token
    When I make an unauthenticated POST request to "/api/cities"
    Then I receive a response with status code 401
