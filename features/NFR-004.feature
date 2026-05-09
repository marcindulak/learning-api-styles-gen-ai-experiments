@status-todo
Feature: NFR-004 Service is testable

  The service ships with end-to-end and integration tests runnable via
  behave-django inside the application container.

  Scenario: behave-django runs the test suite
    Given the service container is running
    When the operator runs "docker compose exec app python manage.py behave --no-input"
    Then the command exits with status 0

  Scenario: Django's own test runner executes
    Given the service container is running
    When the operator runs "docker compose exec app python manage.py test --noinput"
    Then the command exits with status 0
