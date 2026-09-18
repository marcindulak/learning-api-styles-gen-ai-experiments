@status-todo
Feature: FR-004 - Weather alerts via WebSocket
  The service pushes a weather alert to subscribed clients over a
  WebSocket connection when a city's current reading crosses a defined
  threshold: temperature >= 35 degrees Celsius (heat alert), temperature
  <= -10 degrees Celsius (cold alert), or wind speed >= 60 km/h (wind
  alert).

  Background:
    Given the city "São Paulo" exists with uuid "33333333-3333-3333-3333-333333333333"
    And a client has an open WebSocket connection subscribed to alerts for "São Paulo"

  Scenario: Client receives a heat alert when temperature crosses the high threshold
    When "São Paulo" receives a new weather record with temperature 36.0
    Then the subscribed client receives an alert message with type "heat" and city "São Paulo"

  Scenario: Client receives a cold alert when temperature crosses the low threshold
    When "São Paulo" receives a new weather record with temperature -12.0
    Then the subscribed client receives an alert message with type "cold" and city "São Paulo"

  Scenario: Client receives a wind alert when wind speed crosses the threshold
    When "São Paulo" receives a new weather record with wind_speed 65.0
    Then the subscribed client receives an alert message with type "wind" and city "São Paulo"

  Scenario: Client does not receive an alert when readings stay within thresholds
    When "São Paulo" receives a new weather record with temperature 25.0 and wind_speed 10.0
    Then the subscribed client receives no alert message

  Scenario: Client only receives alerts for the city it subscribed to
    Given the city "Mexico City" exists with uuid "44444444-4444-4444-4444-444444444444"
    When "Mexico City" receives a new weather record with temperature 40.0
    Then the client subscribed to "São Paulo" receives no alert message
