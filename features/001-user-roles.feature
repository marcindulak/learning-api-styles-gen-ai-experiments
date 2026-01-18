@status-done
Feature: 001 User Roles and Authentication
  As a system administrator
  I need to manage two types of users (admin and regular user)
  So that the service has proper access control

  Scenario: Admin user can access all features
    Given an admin user exists with username "admin" and password "admin"
    When the admin user logs in
    Then the admin user receives an access token
    And the admin user can access protected endpoints

  Scenario: Regular user can access limited features
    Given a regular user exists with username "user" and password "password"
    When the regular user logs in
    Then the regular user receives an access token
    And the regular user can access only their permitted endpoints
