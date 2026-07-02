@status-done
Feature: FR-002 Service integrates with GitHub via webhooks
  The service exposes a webhook endpoint that accepts GitHub webhook
  deliveries, verifies the HMAC signature using the shared webhook secret,
  and rejects requests with a missing or invalid signature.

  Scenario: Valid GitHub ping webhook delivery is accepted
    Given the service is running
    And the webhook secret is configured from the environment variable "WEBHOOK_SECRET"
    When GitHub sends a POST request to "/api/webhooks/github" with event "ping" and a payload signed with the webhook secret using HMAC SHA-256 in the "X-Hub-Signature-256" header
    Then the response status code is 200
    And the response JSON contains the field "message" with value "pong"

  Scenario: GitHub push webhook delivery is accepted and acknowledged
    Given the service is running
    And the webhook secret is configured from the environment variable "WEBHOOK_SECRET"
    When GitHub sends a POST request to "/api/webhooks/github" with event "push" and a payload signed with the webhook secret using HMAC SHA-256 in the "X-Hub-Signature-256" header
    Then the response status code is 200

  Scenario: Webhook delivery with an invalid signature is rejected
    Given the service is running
    And the webhook secret is configured from the environment variable "WEBHOOK_SECRET"
    When a client sends a POST request to "/api/webhooks/github" with event "push" and the header "X-Hub-Signature-256" set to "sha256=0000000000000000000000000000000000000000000000000000000000000000"
    Then the response status code is 403

  Scenario: Webhook delivery without a signature is rejected
    Given the service is running
    And the webhook secret is configured from the environment variable "WEBHOOK_SECRET"
    When a client sends a POST request to "/api/webhooks/github" with event "push" and no "X-Hub-Signature-256" header
    Then the response status code is 403
