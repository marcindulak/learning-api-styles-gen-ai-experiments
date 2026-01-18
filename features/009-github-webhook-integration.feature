@status-active
Feature: 009 GitHub Webhook Integration
  As a service
  I want to receive and process GitHub webhooks
  So that the service can respond to repository events

  Scenario: GitHub webhook endpoint is accessible
    Given the webhook endpoint exists
    When I make a POST request to the webhook endpoint
    Then the request is accepted with status 200 OK

  Scenario: GitHub webhook payload is validated
    Given a valid GitHub webhook payload
    When I POST the payload to the webhook endpoint
    Then the payload is processed successfully

  Scenario: Invalid GitHub webhook payloads are rejected
    Given an invalid GitHub webhook payload
    When I POST the payload to the webhook endpoint
    Then the request fails with a validation error

  Scenario: GitHub webhook signature is verified
    Given a GitHub webhook with X-Hub-Signature header
    When I POST the webhook payload
    Then the signature is validated against the webhook secret
    And invalid signatures are rejected

  Scenario: Webhook processing does not require authentication
    Given no JWT token is provided
    And a valid GitHub webhook payload
    When I POST to the webhook endpoint
    Then the webhook is processed successfully
