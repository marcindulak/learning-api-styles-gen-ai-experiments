@status-todo
Feature: 008 Weather Alerts via WebSocket
  The service provides real-time weather alerts using WebSocket API
  allowing clients to receive instant notifications

  Scenario: Connect to WebSocket endpoint for weather alerts
    Given the service is running
    When a client connects to WebSocket endpoint "/ws/alerts"
    Then the WebSocket connection is established

  Scenario: Receive weather alert via WebSocket
    Given the service is running
    And a client is connected to WebSocket endpoint "/ws/alerts"
    And the client is subscribed to alerts for city "Tokyo"
    When a weather alert is issued for "Tokyo" with severity "high"
    Then the client receives a WebSocket message with alert for "Tokyo"
    And the alert message contains severity "high"

  Scenario: Subscribe to alerts for specific city
    Given the service is running
    And a client is connected to WebSocket endpoint "/ws/alerts"
    When the client sends subscription message for city "Delhi"
    Then the client receives confirmation of subscription to "Delhi"

  Scenario: Unsubscribe from alerts
    Given the service is running
    And a client is connected to WebSocket endpoint "/ws/alerts"
    And the client is subscribed to alerts for city "Shanghai"
    When the client sends unsubscribe message for city "Shanghai"
    Then the client receives confirmation of unsubscription from "Shanghai"
    When a weather alert is issued for "Shanghai"
    Then the client does not receive the alert message
