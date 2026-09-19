@status-done
Feature: NFR-006 - Service is runnable by a majority of book readers
  The service can be built and run using only Docker and Docker Compose,
  and also runs unmodified inside a GitHub Codespace.

  # Both scenarios below orchestrate `docker compose` itself (building/running
  # a second, independent stack from a fresh clone; standing up the exact
  # stack a GitHub Codespace's automated setup would), which the "app"
  # container has no ability to do to its own sibling stack (no docker
  # CLI/socket access -- see ELN.md ENTRY 015's rejection of
  # Docker-outside-of-Docker for NFR-001 on the same security grounds).
  # Neither scenario has step definitions in features/steps/: they cannot run
  # via `docker compose exec app python manage.py behave` at all, so they are
  # tagged @host-verified and excluded there (see app/behave.ini), and
  # verified instead by standalone scripts run directly on the host/CI
  # runner. See ELN.md ENTRY 017 for the alternatives considered.
  @host-verified
  Scenario: Service builds and runs from a clean checkout using only Docker
    Given a clean checkout of the repository on a machine with only Docker and Docker Compose installed
    When the operator runs "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)" followed by "docker compose up --detach --wait"
    Then the service becomes available at "http://localhost:8000"

  # Verified by tests/codespace_setup_lifecycle.sh: no real GitHub Codespaces
  # access exists in this project's environment, so this exercises the actual
  # mechanism a Codespace delegates to for a docker-compose-based devcontainer
  # (the "dev container spec": read dockerComposeFile/service from
  # .devcontainer/devcontainer.json, then run plain `docker compose up`).
  @host-verified
  Scenario: Service runs inside a GitHub Codespace without manual setup
    Given a new GitHub Codespace is created from the repository
    When the Codespace finishes its automated setup
    Then "docker compose up --detach --wait" succeeds without additional manual configuration
    And the service becomes available on the forwarded port
