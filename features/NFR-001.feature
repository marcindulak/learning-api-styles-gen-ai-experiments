@status-todo
Feature: NFR-001 Service operates in a local environment
  The service runs entirely on the local machine using containers, with no
  dependency on external hosting. All service ports bind to localhost.

  Scenario: The composed service stack runs locally
    Given the project provides a "compose.yaml" file at the repository root
    When the stack is started with "docker compose up --detach --wait"
    Then the container "django-app" is running
    And the container "django-postgres" is running

  Scenario: The application responds on localhost
    Given the service is running
    When a client sends a GET request to "http://localhost:8000/api/health" from the host
    Then the response status code is 200
    And the response JSON contains the field "status" with value "ok"

  Scenario: Service ports are bound to the loopback interface only
    Given the project provides a "compose.yaml" file at the repository root
    When the compose configuration is inspected
    Then every published port of the "app" service is bound to host IP "127.0.0.1"
    And every published port of the "postgres" service is bound to host IP "127.0.0.1"
