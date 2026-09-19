@status-done
Feature: NFR-004 - Service is testable
  The project includes an automated integration test suite and an
  automated end-to-end test suite, each reporting a clear pass/fail
  result via process exit status.

  Scenario Outline: Integration test suite reports its result via exit status
    Given the project's integration test command is available
    When the operator runs a <outcome> integration test suite
    Then the command's exit status reflects that the suite is <outcome>

    Examples:
      | outcome |
      | passing |
      | failing |

  Scenario Outline: End-to-end test suite reports its result via exit status
    Given the service is running via "docker compose up --detach --wait"
    When the operator runs a <outcome> end-to-end test suite against the running service
    Then the command's exit status reflects that the suite is <outcome>

    Examples:
      | outcome |
      | passing |
      | failing |
