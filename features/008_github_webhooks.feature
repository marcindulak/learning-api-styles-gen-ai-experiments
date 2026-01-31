@status-todo
Feature: 008 - GitHub Webhooks Integration

  As an admin of the Weather Forecast Service
  I want to integrate with GitHub via webhooks
  So that I can receive notifications about repository events

  Background:
    Given the Weather Forecast Service is running
    And I have obtained a JWT access token for user "admin"

  Scenario: Receive GitHub push event webhook
    When GitHub sends a push event webhook with a valid signature
    Then I receive a response with status code 200
    And the webhook event is logged in the system

  Scenario: Reject webhook with invalid signature
    When GitHub sends a push event webhook with an invalid signature
    Then I receive a response with status code 401

  Scenario: Receive GitHub pull request event webhook
    When GitHub sends a pull request event webhook with a valid signature
    Then I receive a response with status code 200
    And the webhook event is logged in the system

  Scenario: List received webhook events
    Given a GitHub push event was previously received
    When I request the list of webhook events
    Then I receive a response with status code 200
    And the response contains webhook event details

  Scenario: Webhook endpoint returns correct response headers
    When GitHub sends a push event webhook with a valid signature
    Then I receive a response with status code 200
    And the response contains header "X-GitHub-Hook-Processed" with value "true"
