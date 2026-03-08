@status-done
Feature: 009 GitHub Webhook Integration
  As a weather service operator
  I want to integrate with GitHub webhooks
  So that the system can respond to repository events

  Scenario: Receive GitHub webhook event
    When GitHub sends a webhook POST to "/api/webhooks/github/"
    Then the response status code is 200
    And the webhook event is logged

  Scenario: Validate webhook signature
    Given a webhook secret is configured
    When GitHub sends a signed webhook POST to "/api/webhooks/github/"
    Then the response status code is 200
    And the signature is validated

  Scenario: Reject invalid webhook signature
    Given a webhook secret is configured
    When an invalid signed webhook POST is sent to "/api/webhooks/github/"
    Then the response status code is 401

  Scenario: Trigger data refresh on specific webhook event
    Given a city exists with name "Copenhagen"
    And the third-party weather API is available
    When GitHub sends a webhook for a "data-refresh" event
    Then the response status code is 200
    And weather data for all cities is refreshed

  Scenario: Webhook events are auditable
    When GitHub sends 3 webhook events
    Then the response status code is 200
    And 3 webhook events are logged in the database
