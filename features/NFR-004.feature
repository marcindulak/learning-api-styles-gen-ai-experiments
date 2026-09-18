@status-todo
Feature: NFR-004 - Service is testable
  The project includes an automated integration test suite and an
  automated end-to-end test suite, each reporting a clear pass/fail
  result via process exit status.

  Scenario: Integration test suite runs and reports a result
    Given the project's integration test command is available
    When the operator runs the integration test suite
    Then the command exits with status 0 when all integration tests pass
    And the command exits with a non-zero status when any integration test fails

  Scenario: End-to-end test suite runs and reports a result
    Given the service is running via "docker compose up --detach --wait"
    When the operator runs the end-to-end test suite against the running service
    Then the command exits with status 0 when all end-to-end tests pass
    And the command exits with a non-zero status when any end-to-end test fails
