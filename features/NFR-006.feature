@status-todo
Feature: NFR-006 - Service is runnable by a majority of book readers
  The service can be built and run using only Docker and Docker Compose,
  and also runs unmodified inside a GitHub Codespace.

  Scenario: Service builds and runs from a clean checkout using only Docker
    Given a clean checkout of the repository on a machine with only Docker and Docker Compose installed
    When the operator runs "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)" followed by "docker compose up --detach --wait"
    Then the service becomes available at "http://localhost:8000"

  Scenario: Service runs inside a GitHub Codespace without manual setup
    Given a new GitHub Codespace is created from the repository
    When the Codespace finishes its automated setup
    Then "docker compose up --detach --wait" succeeds without additional manual configuration
    And the service becomes available on the forwarded port
