@status-done
Feature: NFR-003 Service is deployed as one unit

  The Django application is deployed as a single application service in the
  Compose configuration. Supporting services (database, reverse proxy) may
  exist, but the application itself is one service.

  Scenario: Compose configuration declares one application service
    Given the file "compose.yaml" exists at the project root
    When the operator runs "docker compose config --services"
    Then the command output contains a line "app"
    And the command output contains exactly one line that matches the application service "app"

  Scenario: The application service runs the Django process
    Given the service is running
    When the operator runs "docker compose exec app python manage.py check"
    Then the command exits with status 0
