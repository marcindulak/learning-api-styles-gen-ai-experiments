@status-todo
Feature: 009 GitHub Webhooks Integration
  The service integrates with GitHub via webhooks
  allowing automated actions based on GitHub events

  Scenario: Receive GitHub webhook for push event
    Given the service is running
    And a webhook endpoint exists at "/api/webhooks/github"
    When GitHub sends a push event webhook to "/api/webhooks/github"
    Then the webhook is received successfully
    And the response status is 200

  Scenario: Validate GitHub webhook signature
    Given the service is running
    And a webhook secret is configured
    When GitHub sends a webhook with valid signature
    Then the webhook is processed
    When GitHub sends a webhook with invalid signature
    Then the webhook is rejected with status 401

  Scenario: Process GitHub issue event
    Given the service is running
    When GitHub sends an issue opened event webhook
    Then the service logs the issue creation
    And the response status is 200

  Scenario: Process GitHub pull request event
    Given the service is running
    When GitHub sends a pull request opened event webhook
    Then the service logs the pull request creation
    And the response status is 200
