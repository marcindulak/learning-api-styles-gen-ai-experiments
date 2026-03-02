@status-done
Feature: 008 Weather Alerts via WebSocket
  The Weather Forecast Service provides real-time weather alerts via WebSocket.
  Users can subscribe to alerts for specific cities.

  Scenario: Connect to WebSocket endpoint
    Given the service is running
    When I connect to WebSocket "/ws/alerts"
    Then the WebSocket connection is established
    And I receive a welcome message

  Scenario: Subscribe to alerts for a city
    Given the service is running
    And a city "Copenhagen" exists
    And I am connected to WebSocket "/ws/alerts"
    When I send a subscribe message for city "Copenhagen"
    Then I receive a subscription confirmation for "Copenhagen"

  Scenario: Receive alert when weather alert is created
    Given the service is running
    And a city "Copenhagen" exists
    And I am connected to WebSocket "/ws/alerts"
    And I am subscribed to alerts for "Copenhagen"
    When a weather alert is created for "Copenhagen" with severity "high" and message "Strong winds expected"
    Then I receive an alert message for "Copenhagen"
    And the alert contains field "severity" with value "high"
    And the alert contains field "message" with value "Strong winds expected"

  Scenario: Unsubscribe from city alerts
    Given the service is running
    And a city "Copenhagen" exists
    And I am connected to WebSocket "/ws/alerts"
    And I am subscribed to alerts for "Copenhagen"
    When I send an unsubscribe message for city "Copenhagen"
    Then I receive an unsubscribe confirmation for "Copenhagen"
    And I do not receive alerts for "Copenhagen"

  Scenario: Multiple clients receive same alert
    Given the service is running
    And a city "Copenhagen" exists
    And client "A" is connected and subscribed to "Copenhagen"
    And client "B" is connected and subscribed to "Copenhagen"
    When a weather alert is created for "Copenhagen" with severity "medium" and message "Rain expected"
    Then client "A" receives the alert
    And client "B" receives the alert
