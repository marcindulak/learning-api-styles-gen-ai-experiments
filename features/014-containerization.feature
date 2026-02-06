@status-done
Feature: 014 Containerization and Deployment
  Service operates in a local environment using containers
  Service is deployed as one unit (monolith)
  Service is runnable by majority of users

  Scenario: Build service container
    Given Docker is installed
    And the Dockerfile exists at the project root
    When building the container with command "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)"
    Then the container image is built successfully

  Scenario: Run service in container
    Given the service container is built
    When starting the service with command "docker compose up --detach --wait"
    Then the service container is running
    And the service is accessible at "http://localhost:8000"

  Scenario: Service includes PostgreSQL database
    Given the service is running in containers
    When checking running containers
    Then a PostgreSQL container is running
    And the service container is connected to PostgreSQL

  Scenario: Service is deployed as monolith
    Given the service is running in containers
    When checking the deployment architecture
    Then all components run in a single service container
    And the database runs in a separate container
    And both containers are managed by docker compose

  Scenario: Stop service containers
    Given the service is running in containers
    When stopping the service with command "docker compose down"
    Then all service containers are stopped
    And resources are cleaned up
