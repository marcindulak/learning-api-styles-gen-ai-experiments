@status-done
Feature: FR-002 - GitHub webhook receiver
  The service exposes a webhook endpoint that receives GitHub webhook
  events, verifies the payload signature against a shared secret, and
  records accepted events. This is a generic, educational webhook
  receiver and is not tied to weather data.

  Background:
    Given the GitHub webhook secret is configured as "test-webhook-secret"

  Scenario: Accept a GitHub webhook event with a valid signature
    Given a "push" event payload signed with the secret "test-webhook-secret" using HMAC-SHA256
    When a client sends "POST /api/webhooks/github" with the signed payload and header "X-GitHub-Event: push"
    Then the response status is 200
    And an event is recorded with type "push" and a delivery id

  Scenario: Reject a GitHub webhook event with an invalid signature
    Given a "push" event payload signed with the secret "wrong-secret" using HMAC-SHA256
    When a client sends "POST /api/webhooks/github" with the signed payload and header "X-GitHub-Event: push"
    Then the response status is 401
    And no event is recorded

  Scenario: Reject a GitHub webhook event with a missing signature header
    Given a "push" event payload with no "X-Hub-Signature-256" header
    When a client sends "POST /api/webhooks/github" with the unsigned payload and header "X-GitHub-Event: push"
    Then the response status is 401
    And no event is recorded
