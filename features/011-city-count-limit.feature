@status-todo
Feature: 011 City Count Limitation
  As a service
  I want to limit weather data to the 5 biggest cities
  So that the service scope is manageable

  Scenario: System maintains exactly 5 cities
    Given the system is initialized
    When I check the city count
    Then exactly 5 cities are defined in the system

  Scenario: Predefined cities include major world cities
    Given the system is initialized
    When I retrieve the list of predefined cities
    Then the cities include major world population centers
    And each city has valid geographic coordinates

  Scenario: Admin cannot add a 6th city when limit is reached
    Given 5 cities already exist in the system
    When I attempt to create another city
    Then the request is denied with a city limit error

  Scenario: Admin can update predefined cities
    Given 5 cities exist in the system
    When I update the timezone of one city
    Then the city is updated successfully
    And the city count remains 5

  Scenario: Predefined cities cannot be deleted
    Given 5 cities are defined in the system
    When I attempt to delete a city
    Then the deletion is prevented with an error message
