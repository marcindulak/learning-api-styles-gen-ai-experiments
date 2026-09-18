@status-todo
Feature: FR-010 - Two users with object-level permission
  The service distinguishes an admin user from a regular user. Admins
  can create, update, and delete cities and weather records, and can
  view or update any user's profile. Regular users have read-only access
  to weather data and can view or update only their own user profile.

  Background:
    Given an admin user "admin" with password "admin-password"
    And a regular user "alice" with password "alice-password"
    And a regular user "bob" with password "bob-password"
    And "alice" is authenticated with a JWT obtained from "/api/jwt/obtain"

  Scenario: Admin can create a city
    Given "admin" is authenticated with a JWT obtained from "/api/jwt/obtain"
    When "admin" sends "POST /api/cities" to create a city named "Cairo"
    Then the response status is 201

  Scenario: Regular user cannot create a city
    When "alice" sends "POST /api/cities" to create a city named "Cairo"
    Then the response status is 403

  Scenario: Regular user can view their own profile
    When "alice" sends "GET /api/users/alice"
    Then the response status is 200

  Scenario: Regular user cannot view another user's profile
    When "alice" sends "GET /api/users/bob"
    Then the response status is 403

  Scenario: Admin can view any user's profile
    Given "admin" is authenticated with a JWT obtained from "/api/jwt/obtain"
    When "admin" sends "GET /api/users/bob"
    Then the response status is 200

  Scenario: Regular user can view their own profile via GraphQL
    When "alice" sends a "POST /api/graphql" query requesting the user profile for username "alice"
    Then the response status is 200
    And the GraphQL response field "user.username" equals "alice"

  Scenario: Regular user cannot view another user's profile via GraphQL
    When "alice" sends a "POST /api/graphql" query requesting the user profile for username "bob"
    Then the response status is 200
    And the GraphQL response contains an "errors" field
    And the GraphQL response field "user" is null

  Scenario: WebSocket alerts connection requires authentication
    Given the city "Tokyo" exists with uuid "11111111-1111-1111-1111-111111111111"
    When a client attempts to open a WebSocket connection to subscribe to alerts for "Tokyo" without a JWT
    Then the connection is rejected with an authentication error

  Scenario: Authenticated regular user can open a WebSocket alerts connection with their own JWT
    Given the city "Tokyo" exists with uuid "11111111-1111-1111-1111-111111111111"
    When "alice" opens a WebSocket connection to subscribe to alerts for "Tokyo" using her own JWT
    Then the connection is accepted
