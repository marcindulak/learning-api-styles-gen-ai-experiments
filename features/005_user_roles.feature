@status-done
Feature: 005 - User Roles and Permissions

  As the Weather Forecast Service
  I want to differentiate between admin and regular users
  So that only admins can manage cities while regular users can view data

  Background:
    Given the Weather Forecast Service is running

  Scenario: Admin user can create a city
    Given I have obtained a JWT access token for user "admin"
    When I create a city with the following details:
      | name  | country | region | timezone   | latitude  | longitude  |
      | Tokyo | Japan   | Asia   | Asia/Tokyo | 35.689500 | 139.691700 |
    Then I receive a response with status code 201

  Scenario: Regular user cannot create a city
    Given a regular user "viewer" exists with password "viewer123"
    And I have obtained a JWT access token for user "viewer"
    When I create a city with the following details:
      | name  | country | region | timezone   | latitude  | longitude  |
      | Tokyo | Japan   | Asia   | Asia/Tokyo | 35.689500 | 139.691700 |
    Then I receive a response with status code 403

  Scenario: Regular user can view cities
    Given a regular user "viewer" exists with password "viewer123"
    And I have obtained a JWT access token for user "viewer"
    And a city "Tokyo" exists in the system
    When I make an authenticated GET request to "/api/cities"
    Then I receive a response with status code 200

  Scenario: Admin user can delete a city
    Given I have obtained a JWT access token for user "admin"
    And a city "TestCity" exists in the system
    When I delete the city "TestCity"
    Then I receive a response with status code 204

  Scenario: Regular user cannot delete a city
    Given a regular user "viewer" exists with password "viewer123"
    And I have obtained a JWT access token for user "viewer"
    And a city "TestCity" exists in the system
    When I delete the city "TestCity"
    Then I receive a response with status code 403

  Scenario: Admin user can update a city
    Given I have obtained a JWT access token for user "admin"
    And a city "TestCity" exists in the system
    When I update the city "TestCity" with country "TestCountry"
    Then I receive a response with status code 200

  Scenario: Regular user cannot update a city
    Given a regular user "viewer" exists with password "viewer123"
    And I have obtained a JWT access token for user "viewer"
    And a city "TestCity" exists in the system
    When I update the city "TestCity" with country "TestCountry"
    Then I receive a response with status code 403
