@status-todo
Feature: NFR-001 - Service operates in a local environment
  The service and its dependencies run entirely on the local machine via
  containers, without requiring any externally hosted infrastructure
  besides the weather data provider.

  Scenario: Starting the service locally brings up all required containers
    Given the repository is checked out locally
    When the operator runs "docker compose up --detach --wait"
    Then the "app" container reports a healthy status
    And the "db" container reports a healthy status

  Scenario: The running service responds to requests without external orchestration
    Given the service was started with "docker compose up --detach --wait"
    When a client sends "GET /api/cities"
    Then the response status is 200
