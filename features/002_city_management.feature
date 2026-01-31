@status-todo
Feature: 002 - City Management

  As an admin user of the Weather Forecast Service
  I want to manage cities in the system
  So that I can track weather for the 5 biggest cities in the world

  Background:
    Given the Weather Forecast Service is running
    And I have obtained a JWT access token for user "admin"

  Scenario: Create a new city
    When I create a city with the following details:
      | name      | country | region | timezone         | latitude  | longitude |
      | Tokyo     | Japan   | Asia   | Asia/Tokyo       | 35.689500 | 139.691700 |
    Then I receive a response with status code 201
    And the response contains the city name "Tokyo"
    And the response contains a "uuid" field

  Scenario: Retrieve a city by UUID
    Given a city "Delhi" exists in the system
    When I retrieve the city "Delhi" by its UUID
    Then I receive a response with status code 200
    And the response contains the city name "Delhi"

  Scenario: List all cities
    Given the following cities exist in the system:
      | name      | country     | region | timezone              | latitude   | longitude  |
      | Tokyo     | Japan       | Asia   | Asia/Tokyo            | 35.689500  | 139.691700 |
      | Delhi     | India       | Asia   | Asia/Kolkata          | 28.679100  | 77.069700  |
    When I make an authenticated GET request to "/api/cities"
    Then I receive a response with status code 200
    And the response contains a list of cities

  Scenario: Search cities by name
    Given a city "Shanghai" exists in the system
    When I search for cities with name "Shanghai"
    Then I receive a response with status code 200
    And the response contains the city name "Shanghai"

  Scenario: Update a city
    Given a city "SaoPaulo" exists in the system
    When I update the city "SaoPaulo" with country "Brazil"
    Then I receive a response with status code 200
    And the response contains the country "Brazil"

  Scenario: Delete a city
    Given a city "MexicoCity" exists in the system
    When I delete the city "MexicoCity"
    Then I receive a response with status code 204
    And the city "MexicoCity" no longer exists

  Scenario: Limit to 5 cities maximum
    Given the following cities exist in the system:
      | name       | country     | region        | timezone              | latitude   | longitude   |
      | Tokyo      | Japan       | Asia          | Asia/Tokyo            | 35.689500  | 139.691700  |
      | Delhi      | India       | Asia          | Asia/Kolkata          | 28.679100  | 77.069700   |
      | Shanghai   | China       | Asia          | Asia/Shanghai         | 31.224400  | 121.469200  |
      | SaoPaulo   | Brazil      | South America | America/Sao_Paulo     | -23.550520 | -46.633308  |
      | MexicoCity | Mexico      | North America | America/Mexico_City   | 19.432608  | -99.133209  |
    When I create a city with the following details:
      | name   | country | region | timezone       | latitude  | longitude |
      | Mumbai | India   | Asia   | Asia/Kolkata   | 19.076090 | 72.877426 |
    Then I receive a response with status code 400
    And the response contains error message about city limit
