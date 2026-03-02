@status-done
Feature: 012 TLS Support
  The Weather Forecast Service supports both encrypted (HTTPS) and unencrypted (HTTP) requests.
  TLS ensures secure communication for sensitive operations.

  Scenario: Access service via HTTP
    Given the service is running
    When I send a GET request to the full URL "http://localhost:8000/api/cities/"
    Then the response status code is 200

  Scenario: Access service via HTTPS
    Given the service is running with TLS enabled
    When I send a GET request to the full URL "https://localhost:8443/api/cities/"
    Then the response status code is 200
    And the connection is encrypted with TLS

  Scenario: JWT authentication works over HTTPS
    Given the service is running with TLS enabled
    When I send a POST request to the full URL "https://localhost:8443/api/jwt/obtain" with credentials "admin" and "admin"
    Then the response status code is 200
    And the response contains an "access" token
    And the connection is encrypted with TLS

  Scenario: WebSocket connection works over WSS
    Given the service is running with TLS enabled
    When I connect to secure WebSocket "wss://localhost:8443/ws/alerts"
    Then the secure WebSocket connection is established
    And the connection is encrypted with TLS
