@status-todo
Feature: 007 Weather Alerts
  As an API consumer
  I want to receive weather alerts via WebSocket
  So that I can be notified in real-time about severe weather

  Scenario: WebSocket connection can be established for alerts
    Given I am authenticated as a regular user
    When I establish a WebSocket connection to the alerts endpoint
    Then the connection is established successfully
    And the connection status is open

  Scenario: Weather alerts are delivered via WebSocket
    Given I have an active WebSocket connection to the alerts endpoint
    And a severe weather alert is triggered for a city
    When the alert is issued
    Then the alert message is delivered via WebSocket
    And the message includes alert type, city, and description

  Scenario: WebSocket connection can be closed gracefully
    Given I have an active WebSocket connection to the alerts endpoint
    When I close the WebSocket connection
    Then the connection is closed successfully
    And subsequent messages are not received

  Scenario: Unauthenticated users cannot connect to alerts endpoint
    Given no JWT token is provided
    When I attempt to establish a WebSocket connection to the alerts endpoint
    Then the connection is rejected with an authentication error

  Scenario: Multiple users can receive alerts simultaneously
    Given 3 authenticated users have WebSocket connections to the alerts endpoint
    When a weather alert is triggered
    Then all 3 users receive the alert message
