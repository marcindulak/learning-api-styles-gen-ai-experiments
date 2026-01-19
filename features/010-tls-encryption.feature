@status-done
Feature: 010 TLS Encryption Support
  As a security-conscious client
  I need to communicate with the service using TLS encryption
  So that data in transit is protected

  Scenario: Service accepts encrypted HTTPS requests
    Given the service is running with TLS certificates installed
    When a client sends a request via HTTPS
    Then the TLS handshake completes successfully
    And the request is processed normally
    And the response is returned over the encrypted connection

  Scenario: Service accepts both encrypted and unencrypted requests
    Given the service is configured to accept both HTTP and HTTPS
    When a client sends a request via HTTP (unencrypted)
    Then the request is accepted and processed
    And the response is returned via HTTP
