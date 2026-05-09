@status-todo
Feature: NFR-001 Service operates in a local environment

  The service can be built and started on a developer's local machine using
  Docker Compose, without dependencies on a remote environment.

  Scenario: Service starts via Docker Compose and answers a request
    Given the project repository is checked out locally
    And Docker and the Docker Compose plugin are installed
    And the operator has run "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)" successfully
    And the operator has run "docker compose up --detach --wait" successfully
    When a client sends GET to "http://localhost:8000/api/cities"
    Then the response status is 200
