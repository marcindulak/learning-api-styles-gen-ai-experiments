@status-done
Feature: NFR-002 Service requests can be encrypted or unencrypted

  The service accepts both unencrypted HTTP requests on port 8000 and
  TLS-encrypted HTTPS requests on port 8443.

  Scenario: Service answers an unencrypted HTTP request
    Given the service is running with HTTP on port 8000 and HTTPS on port 8443
    When a client sends GET to "http://localhost:8000/api/cities"
    Then the response status is 200

  Scenario: Service answers an encrypted HTTPS request
    Given the service is running with HTTP on port 8000 and HTTPS on port 8443
    When a client sends GET to "https://localhost:8443/api/cities" trusting the service certificate
    Then the TLS handshake succeeds
    And the response status is 200
