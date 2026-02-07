@status-done
Feature: 015 Testing Framework
  The service is testable using behave-django
  Tests can be executed within the running container

  Scenario: Run behave tests in container
    Given the service is running in containers
    When executing command "docker compose exec app python manage.py behave --no-input"
    Then all behave tests are executed
    And test results are displayed

  Scenario: Tests verify service functionality
    Given the service is running in containers
    And feature files exist in features/ directory
    When running behave tests
    Then each feature scenario is tested
    And passing tests are marked as passed
    And failing tests are marked as failed with details

  Scenario: Integration tests use test database
    Given the service is running in containers
    When running behave tests
    Then a separate test database is created
    And tests run in isolation from production data
    And the test database is cleaned up after tests

  Scenario: End-to-end tests using curl
    Given the service is running in containers
    When executing curl commands from within the container
    Then API endpoints can be tested directly
    And responses can be validated using jq
