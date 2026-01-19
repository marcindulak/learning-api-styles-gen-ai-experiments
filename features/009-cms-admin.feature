@status-done
Feature: 009 Content Management System
  As an admin user
  I need a content management system
  So that I can manage service configuration and content

  Scenario: Admin accesses CMS dashboard
    Given an admin user is authenticated
    When the admin user navigates to the CMS dashboard
    Then the dashboard loads successfully
    And the admin can see options to manage cities, weather data, and alerts

  Scenario: Admin creates content through CMS
    Given an admin user is on the CMS dashboard
    When the admin creates a new weather alert with title and message
    Then the content is saved in the database
    And the content is immediately available through the APIs
