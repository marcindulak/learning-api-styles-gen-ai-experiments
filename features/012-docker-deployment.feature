@status-done
Feature: 012 Docker Deployment
  As an operator
  I want to deploy the service using Docker
  So that the application can run in a containerized environment

  Scenario: Docker Compose configuration exists
    Given the project root directory
    When I check for Docker Compose configuration
    Then a compose.yaml file exists
    And the file contains valid Docker Compose syntax

  Scenario: Application can be built with Docker
    Given a valid Dockerfile exists
    When I build the Docker image with proper UID and GID arguments
    Then the build completes successfully
    And the image contains the Python application

  Scenario: Service starts with Docker Compose
    Given the Docker image has been built
    When I run "docker compose up --detach --wait"
    Then all services start successfully
    And health checks pass

  Scenario: Database service is included in Docker Compose
    Given a compose.yaml file exists
    When I inspect the Docker Compose configuration
    Then a PostgreSQL service is defined
    And the service has proper environment variables configured

  Scenario: Application container exposes correct ports
    Given the application is running in Docker
    When I check the exposed ports
    Then port 8000 is exposed for the Django application
