@status-done
Feature: 008 Weather Alerts via WebSocket
  As a weather service user
  I want to receive real-time weather alerts
  So that I can be notified immediately of severe weather

  Scenario: Connect to WebSocket for weather alerts
    When I establish a WebSocket connection to "/ws/alerts/"
    Then the WebSocket connection is successful

  Scenario: Subscribe to alerts for a specific city
    Given I have a WebSocket connection to "/ws/alerts/"
    When I send a subscribe message for "Copenhagen"
    Then I receive a confirmation message

  Scenario: Receive weather alert for subscribed city
    Given I have a WebSocket connection to "/ws/alerts/"
    And I am subscribed to alerts for "Tokyo"
    When a weather alert is issued for "Tokyo"
    Then I receive the alert via WebSocket

  Scenario: Multiple clients receive the same alert
    Given client A and client B are connected to "/ws/alerts/"
    And both are subscribed to alerts for "London"
    When a weather alert is issued for "London"
    Then both client A and client B receive the alert

  Scenario: Unsubscribe from city alerts
    Given I have a WebSocket connection to "/ws/alerts/"
    And I am subscribed to alerts for "Paris"
    When I send an unsubscribe message for "Paris"
    And a weather alert is issued for "Paris"
    Then I do not receive the alert
