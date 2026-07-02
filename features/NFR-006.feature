@status-done
Feature: NFR-006 Service is runnable by a majority of book readers
  A reader can start the whole service with the two documented docker
  compose commands, without installing language toolchains on the host,
  and can also run it in GitHub Codespaces via a devcontainer definition.

  Scenario: The service starts with the two documented commands
    Given the project provides a "compose.yaml" file at the repository root
    And the project provides a "Dockerfile" at the repository root
    And the stack was built with "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)"
    When the stack is started with "docker compose up --detach --wait"
    And a client sends a GET request to "http://localhost:8000/api/health" from the host
    Then the container "django-app" is running
    And the container "django-postgres" is running
    And the response status code is 200

  Scenario: The README documents how to run the service
    Given a checkout of the repository
    When the file "README.md" is read
    Then it contains the command "docker compose build"
    And it contains the command "docker compose up"
    And it contains the command "python manage.py behave"

  Scenario: A devcontainer definition is provided for GitHub Codespaces
    Given a checkout of the repository
    When the file ".devcontainer/devcontainer.json" is read
    Then it is a valid JSON document
    And it references the "compose.yaml" file
    And it sets the service to "app"
