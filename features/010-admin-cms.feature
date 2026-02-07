@status-done
Feature: 010 Admin Content Management System
  The service has a content management system for admin users
  using Django's built-in admin interface

  Scenario: Admin can access Django admin interface
    Given the service is running
    And an admin user exists with username "admin" and password "admin"
    When the admin user navigates to "/admin"
    And logs in with username "admin" and password "admin"
    Then the admin user sees the Django admin dashboard

  Scenario: Admin can manage cities through CMS
    Given the service is running
    And an admin user is logged into the admin interface
    When the admin navigates to the cities section
    Then the admin sees a list of cities
    And the admin can add a new city
    And the admin can edit existing cities
    And the admin can delete cities

  Scenario: Admin can manage users through CMS
    Given the service is running
    And an admin user is logged into the admin interface
    When the admin navigates to the users section
    Then the admin sees a list of users
    And the admin can create new users
    And the admin can modify user permissions

  Scenario: Admin can manage weather records through CMS
    Given the service is running
    And an admin user is logged into the admin interface
    When the admin navigates to the weather records section
    Then the admin sees a list of weather records
    And the admin can filter records by city
    And the admin can view record details
