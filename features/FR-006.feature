@status-done
Feature: FR-006 - Content management system for the admin user
  The service provides a content management system, implemented as the
  Django admin site, through which the admin user manages cities and
  weather records. Regular users cannot access it.

  Background:
    Given an admin user "admin" with password "admin-password"
    And a regular user "alice" with password "alice-password"

  Scenario: Admin logs into the CMS
    When "admin" logs into "/admin/" with password "admin-password"
    Then the login succeeds
    And the CMS dashboard lists the "Cities" and "Weather records" sections

  Scenario: Admin creates a city via the CMS
    Given "admin" is logged into "/admin/"
    When "admin" creates a city named "Cairo" via the CMS
    Then a city named "Cairo" exists in the service

  Scenario: Admin creates a weather record via the CMS
    Given "admin" is logged into "/admin/"
    And the city "Cairo" exists
    When "admin" creates a weather record for "Cairo" with temperature 30.0 via the CMS
    Then a weather record for "Cairo" with temperature 30.0 exists in the service

  Scenario: Regular user cannot access the CMS
    When "alice" attempts to log into "/admin/" with password "alice-password"
    Then the login is rejected
    And "alice" is not shown the CMS dashboard
