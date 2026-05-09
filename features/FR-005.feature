@status-todo
Feature: FR-005 Weather alerts via WebSocket

  The service publishes weather alerts to subscribers over a WebSocket
  connection at "/ws/alerts".

  Scenario: Subscriber receives a published weather alert
    Given the service is running
    And a client is connected to the WebSocket "/ws/alerts"
    When an admin publishes a weather alert with text "Storm warning for Tokyo"
    Then the connected client receives a message with text "Storm warning for Tokyo" within 5 seconds

  Scenario: WebSocket connection on an unknown path is closed
    Given the service is running
    When a client opens a WebSocket connection to "/ws/unknown"
    Then the WebSocket handshake fails with HTTP status 404
