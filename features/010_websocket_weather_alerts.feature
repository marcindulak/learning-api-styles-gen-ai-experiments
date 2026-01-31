@status-done
Feature: 010 - WebSocket Weather Alerts

  As a user of the Weather Forecast Service
  I want to receive real-time weather alerts via WebSocket
  So that I can be notified immediately of severe weather conditions

  Background:
    Given the Weather Forecast Service is running
    And a city "Tokyo" exists in the system

  Scenario: Connect to WebSocket weather alerts endpoint
    When I connect to the WebSocket alerts endpoint for city "Tokyo"
    Then the WebSocket connection is established successfully
    And I receive a connection confirmation message

  Scenario: Receive weather alert via WebSocket
    Given I am connected to the WebSocket alerts endpoint for city "Tokyo"
    When a weather alert is triggered for city "Tokyo"
    Then I receive a WebSocket message containing the alert
    And the alert contains severity level
    And the alert contains alert description
    And the alert contains timestamp

  Scenario: Weather alert contains city information
    Given I am connected to the WebSocket alerts endpoint for city "Tokyo"
    When a weather alert is triggered for city "Tokyo"
    Then I receive a WebSocket message containing the alert
    And the alert contains city UUID
    And the alert contains city name

  Scenario: Disconnect from WebSocket gracefully
    Given I am connected to the WebSocket alerts endpoint for city "Tokyo"
    When I close the WebSocket connection
    Then the WebSocket connection is closed successfully

  Scenario: Reject WebSocket connection for non-existent city
    When I connect to the WebSocket alerts endpoint for non-existent city UUID "00000000-0000-0000-0000-000000000000"
    Then the WebSocket connection is rejected
    And I receive an error message about invalid city
