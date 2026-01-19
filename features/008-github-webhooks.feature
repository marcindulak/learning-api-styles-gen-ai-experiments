@status-done
Feature: 008 GitHub Webhook Integration
  As a system administrator
  I need to integrate with GitHub via webhooks
  So that the service can respond to repository events

  Scenario: Receive and process GitHub webhook event
    Given a GitHub repository is configured with a webhook pointing to the service
    And the webhook is set to trigger on push events
    When a push event occurs on the repository
    Then the service receives the webhook payload
    And the service processes the event successfully
    And the service returns HTTP 200 OK to GitHub

  Scenario: Webhook authenticates with GitHub signature
    Given a webhook endpoint exists at /webhooks/github
    When a webhook request is received with a valid GitHub signature
    Then the signature is verified against the webhook secret
    And the request is processed as authentic
    And the payload is used to trigger appropriate actions
