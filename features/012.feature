@status-done
Feature: 012 TLS Support
  As a security-conscious user
  I want the service to support encrypted connections
  So that data transmission is secure

  Scenario: Service is accessible via HTTP
    When I send a GET request to the full URL "http://localhost:8000/admin/"
    Then the response status code is 200

  Scenario: Service is accessible via HTTPS
    Given TLS is enabled
    When I send a GET request to the full URL "https://localhost:8443/admin/"
    Then the response status code is 200
    And the connection uses TLS encryption

  Scenario: JWT authentication works over HTTPS
    Given TLS is enabled
    When I request a JWT access token over HTTPS with username "admin" and password "admin"
    Then the response status code is 200
    And the response contains a field "access"

  Scenario: WebSocket Secure connection works
    Given TLS is enabled
    When I establish a secure WebSocket connection to "wss://localhost:8443/ws/alerts/"
    Then the WebSocket connection is successful
    And the connection uses WSS protocol
