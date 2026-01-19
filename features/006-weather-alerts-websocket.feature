@status-done
Feature: 006 Weather Alerts via WebSocket
  As a client application
  I need to receive real-time weather alerts
  So that I can notify users of severe weather conditions

  Scenario: Client connects to WebSocket for alerts
    Given a city "Copenhagen" exists in the system
    When the client establishes a WebSocket connection to /ws/alerts?city=Copenhagen
    Then the connection is established with HTTP 101 Switching Protocols
    And the client is ready to receive alert messages

  Scenario: Receive alert when severe weather occurs
    Given a client is connected to the WebSocket alerts endpoint for "Copenhagen"
    And a severe weather condition is detected (e.g., storm warning)
    When the severe weather event occurs
    Then the server sends an alert message via WebSocket
    And the alert contains event type, description, and timestamp
    And the client receives the alert without polling
