@status-done
Feature: NFR-004 Service is testable
  The service ships with an automated test setup: behave-django executes
  the Gherkin scenarios as integration tests inside the running container,
  and end-to-end tests can be performed with curl against the running
  service.

  Scenario: The behave test runner is available in the container
    Given the service is running
    When the command "python manage.py behave --dry-run --no-input" is executed in the "app" container
    Then the command exits with status code 0
    And the output reports 0 undefined steps

  Scenario: A Gherkin feature is executable as an integration test
    Given the service is running
    When the command "python manage.py behave --include FR-001 --no-input" is executed in the "app" container
    Then the command exits with status code 0
    And the output reports 0 failed scenarios

  Scenario: An end-to-end test can be performed with curl
    Given the service is running
    When the command "curl --silent --fail http://localhost:8000/api/health" is executed in the "app" container
    Then the command exits with status code 0
    And the command output is valid JSON
