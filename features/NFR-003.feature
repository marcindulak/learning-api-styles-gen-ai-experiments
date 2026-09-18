@status-todo
Feature: NFR-003 - Service is deployed as one unit
  All service APIs (REST, GraphQL, Atom feed, WebSocket, webhooks, CMS)
  are served by a single deployable application container, rather than
  as independently deployed services.

  Scenario: A single container serves every API
    Given the service is running via "docker compose up --detach --wait"
    When a client sends "GET /api/cities" and "POST /api/graphql" and "GET /admin/"
    Then all three requests are handled by the same "app" container
    And no additional application container is required to serve any of them

  Scenario: The application starts and stops as a single unit
    Given the service is running via "docker compose up --detach --wait"
    When the operator runs "docker compose stop app"
    Then the REST, GraphQL, Atom, WebSocket, webhook, and CMS endpoints all become unavailable together
