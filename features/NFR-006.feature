@status-todo
Feature: NFR-006 Service is runnable by a majority of book readers
  A reader can start the whole service with the two documented docker
  compose commands, without installing language toolchains on the host,
  and can also run it in GitHub Codespaces via a devcontainer definition.

  Scenario: The service starts with the two documented commands
    Given a checkout of the repository on a host with Docker installed
    When the command "docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)" is executed at the repository root
    And the command "docker compose up --detach --wait" is executed at the repository root
    Then both commands exit with status code 0
    And a GET request to "http://localhost:8000/api/health" returns status code 200

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
