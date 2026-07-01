@status-todo
Feature: NFR-003 Service is deployed as one unit
  The service is a monolith: a single application container provides all
  APIs (REST, GraphQL, Atom feed, WebSocket, webhooks, CMS), backed by
  supporting infrastructure containers only.

  Scenario: The compose stack contains exactly one application service
    Given the project provides a "compose.yaml" file at the repository root
    When the compose configuration is inspected
    Then exactly one service builds from the project Dockerfile
    And that service is named "app"

  Scenario: All APIs are served by the single application container
    Given the service is running
    When a client sends a GET request to "http://localhost:8000/api/health"
    And a client sends a POST request to "http://localhost:8000/graphql" with a valid GraphQL introspection query
    And a client sends a GET request to "http://localhost:8000/admin/login/"
    And a client opens a WebSocket connection to "/ws/alerts"
    Then all HTTP responses have status code 200
    And the WebSocket handshake succeeds
    And all endpoints are served by the container "django-app"

  Scenario: The application is built as a single image
    Given the project provides a "Dockerfile" at the repository root
    When the compose configuration is inspected
    Then the "app" service uses the image "django/app"
