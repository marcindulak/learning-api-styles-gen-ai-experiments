@status-todo
Feature: NFR-002 - Requests can be encrypted or unencrypted
  The service accepts requests over both plain HTTP and TLS-encrypted
  HTTPS.

  Scenario: Service accepts an unencrypted HTTP request
    When a client sends "GET http://localhost:8000/api/cities"
    Then the response status is 200

  Scenario: Service accepts a TLS-encrypted HTTPS request
    When a client sends "GET https://localhost:8443/api/cities"
    Then the response status is 200
    And the connection was established using TLS
