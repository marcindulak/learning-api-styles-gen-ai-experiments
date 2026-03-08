@status-done
Feature: 013 Containerized Deployment
  As a developer or operator
  I want to deploy the service using containers
  So that the service runs in a consistent, isolated environment

  Scenario: Service containers can be built
    When I build the Docker containers
    Then the build completes successfully
    And the app container image exists

  Scenario: Service containers can start
    When I start the service with docker compose
    Then the app container is running
    And the database container is running

  Scenario: Service is accessible within containers
    Given the service containers are running
    When I send a request to the service from within the container
    Then the response indicates the service is healthy

  Scenario: Service can be stopped
    Given the service containers are running
    When I stop the service with docker compose
    Then no service containers are running

  Scenario: Data persists across container restarts
    Given the service containers are running
    And data exists in the database
    When I restart the service containers
    Then the data is still present in the database
