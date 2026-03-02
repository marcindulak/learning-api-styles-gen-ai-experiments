@status-done
Feature: 009 GitHub Webhook Integration
  The Weather Forecast Service integrates with GitHub via webhooks.
  Webhooks can trigger actions such as data refresh or logging events.

  Scenario: Receive GitHub push webhook
    Given the service is running
    When GitHub sends a push webhook to "/webhooks/github" with payload:
      | repository | weather-data-repo |
      | ref        | refs/heads/main   |
      | pusher     | testuser          |
    Then the response status code is 200
    And the webhook event is logged

  Scenario: Validate GitHub webhook signature
    Given the service is running
    And a webhook secret is configured
    When GitHub sends a webhook with valid signature
    Then the response status code is 200
    And the webhook is processed

  Scenario: Reject webhook with invalid signature
    Given the service is running
    And a webhook secret is configured
    When a webhook is sent with invalid signature
    Then the response status code is 401
    And the webhook is not processed

  Scenario: Trigger data refresh on specific webhook event
    Given the service is running
    And a city "Copenhagen" exists
    When GitHub sends a push webhook to "/webhooks/github" with tag "data-refresh"
    Then the response status code is 200
    And weather data fetch is triggered for all cities

  Scenario: Log webhook events for audit
    Given the service is running
    When GitHub sends any webhook to "/webhooks/github"
    Then the response status code is 200
    And the webhook event is stored with timestamp, event type, and payload
