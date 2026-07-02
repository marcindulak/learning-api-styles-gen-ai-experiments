@status-done
Feature: FR-004 Service provides weather alerts
  The service broadcasts weather alerts to connected clients over a
  WebSocket API, so that clients receive alerts as they are published.

  Scenario: Client receives a weather alert over WebSocket
    Given the service is running
    And a city named "Tokyo" exists
    And a client is connected to the WebSocket endpoint "/ws/alerts"
    When a weather alert with title "Heavy rain" and severity "warning" is published for the city "Tokyo"
    Then the connected client receives a JSON message within 5 seconds
    And the message contains the field "title" with value "Heavy rain"
    And the message contains the field "severity" with value "warning"
    And the message contains the field "city" with value "Tokyo"

  Scenario: Multiple connected clients receive the same alert
    Given the service is running
    And a city named "Tokyo" exists
    And 2 clients are connected to the WebSocket endpoint "/ws/alerts"
    When a weather alert with title "Heat wave" and severity "critical" is published for the city "Tokyo"
    Then each connected client receives a JSON message within 5 seconds
    And each received message contains the field "title" with value "Heat wave"

  Scenario: WebSocket connection to the alerts endpoint is accepted
    Given the service is running
    When a client opens a WebSocket connection to "/ws/alerts"
    Then the WebSocket handshake succeeds
