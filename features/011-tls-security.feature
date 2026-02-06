@status-todo
Feature: 011 TLS Security
  Service requests can be encrypted or unencrypted
  The service supports both HTTP and HTTPS connections

  Scenario: Service accepts HTTP requests
    Given the service is running
    When sending an HTTP request to "http://localhost:8000/api/cities"
    Then the request is processed successfully

  Scenario: Service accepts HTTPS requests when TLS is configured
    Given the service is running with TLS enabled
    When sending an HTTPS request to "https://localhost:8443/api/cities"
    Then the request is processed successfully
    And the connection is encrypted

  Scenario: TLS configuration is optional
    Given the service is running without TLS
    When checking service configuration
    Then HTTP endpoint is available
    And HTTPS endpoint is not available
