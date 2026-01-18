@status-done
Feature: 010 TLS Encryption Support
  As a service
  I want to support both encrypted and unencrypted requests
  So that clients can choose their communication method

  Scenario: Service accepts encrypted HTTPS requests
    Given the service is running with TLS enabled
    When I make an HTTPS request to the API
    Then the request is successful
    And the response is encrypted

  Scenario: Service accepts unencrypted HTTP requests
    Given the service is running
    When I make an HTTP request to the API
    Then the request is successful
    And the response is received

  Scenario: TLS certificate is valid
    Given the service is running with HTTPS
    When I verify the TLS certificate
    Then the certificate is valid
    And certificate chain is complete

  Scenario: Service supports modern TLS versions
    Given the service is configured with TLS
    When I attempt connection with TLS 1.2 or higher
    Then the connection is established successfully

  Scenario: Weak TLS versions are not accepted
    Given the service is configured with TLS
    When I attempt connection with TLS 1.0
    Then the connection is rejected
