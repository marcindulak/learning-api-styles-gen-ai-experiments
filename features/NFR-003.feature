@status-done
Feature: NFR-003 - Service is deployed as one unit
  All service APIs (REST, GraphQL, Atom feed, WebSocket, webhooks, CMS)
  are served by a single deployable application container, rather than
  as independently deployed services.

  Scenario: A single container serves every API
    Given the service is running via "docker compose up --detach --wait"
    When a client sends "GET /api/cities" and "POST /api/graphql" and "GET /admin/"
    Then all three requests are handled by the same "app" container
    And no additional application container is required to serve any of them

  # Verified by tests/single_unit_lifecycle.sh, run directly on the host/CI
  # runner rather than through "docker compose exec app python manage.py
  # behave": stopping app would kill that in-container behave process before
  # it could observe the fact this scenario is about. See app/behave.ini for
  # the matching tag exclusion and ELN.md ENTRY 016 for the alternatives
  # considered (a docker-socket-proxy sidecar; installing behave on the host).
  @host-verified
  Scenario: The application starts and stops as a single unit
    Given the service is running via "docker compose up --detach --wait"
    When the operator runs "docker compose stop app"
    Then the REST, GraphQL, Atom, WebSocket, webhook, and CMS endpoints all become unavailable together
