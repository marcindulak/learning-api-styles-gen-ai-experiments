@status-todo
Feature: FR-003 GitHub webhook integration

  The service exposes a webhook endpoint that GitHub can call. The endpoint
  verifies the HMAC SHA-256 signature using a shared secret and records valid
  events.

  Scenario: Accept a GitHub webhook event with a valid signature
    Given the service is running
    And the GitHub webhook secret is configured to "s3cret"
    When GitHub sends a "push" event to "/webhooks/github" signed with "s3cret"
    Then the response status is 202
    And the event is recorded in the webhook log

  Scenario: Reject a GitHub webhook event with an invalid signature
    Given the service is running
    And the GitHub webhook secret is configured to "s3cret"
    When GitHub sends a "push" event to "/webhooks/github" signed with "wrong"
    Then the response status is 401
    And the event is not recorded in the webhook log

  Scenario: Reject a GitHub webhook event without a signature header
    Given the service is running
    And the GitHub webhook secret is configured to "s3cret"
    When GitHub sends a "push" event to "/webhooks/github" without a signature header
    Then the response status is 401
    And the event is not recorded in the webhook log
