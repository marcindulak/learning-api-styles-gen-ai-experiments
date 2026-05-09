@status-done
Feature: NFR-006 Service is runnable by majority of book readers

  Beyond local Docker Compose, the project provides a devcontainer
  configuration so it can be opened in GitHub Codespaces with a single click.

  Scenario: Repository contains a devcontainer configuration
    Given the project repository is checked out
    When the operator inspects the repository
    Then the file ".devcontainer/devcontainer.json" exists
    And ".devcontainer/devcontainer.json" references the project's "compose.yaml"

  Scenario: Repository contains container build instructions
    Given the project repository is checked out
    When the operator inspects the repository
    Then the file "Dockerfile" exists at the project root
    And the file "compose.yaml" exists at the project root
