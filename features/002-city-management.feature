@status-todo
Feature: 002 City Management
  Weather data is limited to the 5 biggest cities in the world
  Cities must be manageable through the system

  Scenario: System limits weather data to 5 biggest cities
    Given the service is running
    And the following cities exist in the system:
      | name       | country | region | timezone           | latitude | longitude |
      | Tokyo      | Japan   | Asia   | Asia/Tokyo         | 35.6762  | 139.6503  |
      | Delhi      | India   | Asia   | Asia/Kolkata       | 28.7041  | 77.1025   |
      | Shanghai   | China   | Asia   | Asia/Shanghai      | 31.2304  | 121.4737  |
      | Sao Paulo  | Brazil  | SA     | America/Sao_Paulo  | -23.5505 | -46.6333  |
      | Mexico City| Mexico  | NA     | America/Mexico_City| 19.4326  | -99.1332  |
    When the system retrieves the list of cities
    Then exactly 5 cities are returned

  Scenario: Retrieve city by name
    Given the service is running
    And a city "Tokyo" with country "Japan" exists
    When searching for city with name "Tokyo"
    Then the city "Tokyo" is returned with country "Japan"

  Scenario: Retrieve city by UUID
    Given the service is running
    And a city "Delhi" with UUID "550e8400-e29b-41d4-a716-446655440000" exists
    When retrieving city by UUID "550e8400-e29b-41d4-a716-446655440000"
    Then the city "Delhi" is returned
