Feature: GitHub webhook integration
  As a developer
  I want to receive GitHub webhook events
  So that the service can respond to repository events

  Scenario: Valid webhook with ping event
    When I POST a webhook ping event with valid signature
    Then the response status is 200
    And the response contains "pong"

  Scenario: Webhook with invalid signature
    When I POST a webhook event with invalid signature
    Then the response status is 403
