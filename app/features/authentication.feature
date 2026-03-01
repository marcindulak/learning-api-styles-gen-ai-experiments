Feature: JWT Authentication
  As a user
  I want to authenticate using JWT tokens
  So that I can access protected resources

  Scenario: Obtain JWT token with valid credentials
    Given I have valid admin credentials
    When I request a JWT token
    Then I should receive an access token
    And I should receive a refresh token

  Scenario: Access protected endpoint with valid token
    Given I have a valid JWT access token
    When I access a protected endpoint
    Then I should receive a successful response

  Scenario: Access protected endpoint without token
    Given I do not have a JWT token
    When I try to create a city
    Then I should receive an unauthorized response
