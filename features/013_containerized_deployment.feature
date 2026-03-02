@status-done
Feature: 013 Containerized Deployment
  The Weather Forecast Service operates in a local containerized environment.
  The service is deployed as a monolithic unit using Docker containers.

  Scenario: Build Docker containers
    Given the project source code exists
    When I run "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)"
    Then the build completes successfully
    And the "app" container image is created

  Scenario: Start services with Docker Compose
    Given the Docker containers are built
    When I run "docker compose up --detach --wait"
    Then the "app" service is running
    And the "db" service is running
    And the service is accessible at "http://localhost:8000"

  Scenario: Service connects to PostgreSQL database
    Given the Docker containers are running
    When the "app" service starts
    Then the service connects to PostgreSQL on the "db" container
    And database migrations are applied

  Scenario: Stop services with Docker Compose
    Given the Docker containers are running
    When I run "docker compose down"
    Then all services are stopped
    And containers are removed

  Scenario: Service persists data across restarts
    Given the Docker containers are running
    And a city "Copenhagen" is created
    When I run "docker compose down"
    And I run "docker compose up --detach --wait"
    Then the city "Copenhagen" still exists in the database
