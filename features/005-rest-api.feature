@status-todo
Feature: 005 REST API for Weather Indicators
  The service exposes common weather indicators via REST API
  Authentication is performed using JWT tokens

  Scenario: Obtain JWT access token
    Given the service is running
    And an admin user exists with username "admin" and password "admin"
    When requesting JWT token with username "admin" and password "admin"
    Then a valid JWT access token is returned

  Scenario: Create city via REST API
    Given the service is running
    And an admin user is authenticated with JWT token
    When creating a city via POST to "/api/cities" with data:
      | name       | country | region | timezone           | latitude | longitude |
      | Copenhagen | Denmark | Europe | Europe/Copenhagen  | 55.6761  | 12.5683   |
    Then the response status is 201
    And the response contains city UUID
    And the response contains city name "Copenhagen"

  Scenario: Read city via REST API
    Given the service is running
    And a city "Copenhagen" with UUID "550e8400-e29b-41d4-a716-446655440001" exists
    When retrieving city via GET from "/api/cities/550e8400-e29b-41d4-a716-446655440001"
    Then the response status is 200
    And the response contains city name "Copenhagen"

  Scenario: Search cities via REST API
    Given the service is running
    And a city "Copenhagen" exists
    When searching cities via GET from "/api/cities?search_name=Copenhagen"
    Then the response status is 200
    And the results contain city "Copenhagen"

  Scenario: Update city via REST API
    Given the service is running
    And an admin user is authenticated with JWT token
    And a city "Copenhagen" with UUID "550e8400-e29b-41d4-a716-446655440001" exists
    When updating city via PATCH to "/api/cities/550e8400-e29b-41d4-a716-446655440001" with data:
      | latitude | longitude |
      | 55.7000  | 12.6000   |
    Then the response status is 200
    And the response contains updated latitude 55.7000

  Scenario: Delete city via REST API
    Given the service is running
    And an admin user is authenticated with JWT token
    And a city "Copenhagen" with UUID "550e8400-e29b-41d4-a716-446655440001" exists
    When deleting city via DELETE from "/api/cities/550e8400-e29b-41d4-a716-446655440001"
    Then the response status is 204
    And the city "Copenhagen" no longer exists in the system
