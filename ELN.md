# Electronic Lab Notebook

This is an append-only log for human review only. Each entry documents observations and learnings from implementing features.

---

# Start of ENTRY 001
DATE: 2026-01-31 02:14:21
TITLE: Generate features from REQUIREMENTS.md
COMMIT: 0f56adf
OBSERVATIONS: Created 6 Gherkin feature files covering the core Weather Forecast Service functionality based on REQUIREMENTS.md analysis. The features cover: JWT authentication (001), city management with 5-city limit (002), weather forecasts with 7-day limit (003), historical weather data (004), user roles and permissions for admin vs regular users (005), and REST API weather indicators (006). Some advanced requirements (webhooks, Atom feed, WebSocket alerts) were deferred as they require additional infrastructure beyond the core REST API. All feature scenarios are concrete and testable with specific status codes and field validations. The features follow a logical dependency order where authentication (001) is prerequisite for most other features.
# End of ENTRY 001

# Start of ENTRY 002
DATE: 2026-01-31 02:49:00
TITLE: Implement Feature 001: JWT Authentication
COMMIT: 0c2edcb
OBSERVATIONS: Successfully implemented JWT authentication for the Weather Forecast Service. The implementation uses Django REST Framework SimpleJWT for token generation and validation. Key components include: authentication URLs for token obtain/refresh endpoints, step definitions for BDD testing, and environment setup for behave tests. Fixed an issue with trailing slashes causing 301 redirects - resolved by setting APPEND_SLASH=False and configuring DefaultRouter with trailing_slash=False. The compose.yaml was updated to mount the features directory into the container for test execution. All 4 scenarios pass: obtaining valid tokens, rejecting invalid credentials, accessing protected endpoints with valid tokens, and rejecting unauthenticated requests. The admin user is created via test fixtures with username/password "admin"/"admin".
# End of ENTRY 002

# Start of ENTRY 003
DATE: 2026-01-31 03:21:00
TITLE: Implement Feature 002: City Management
COMMIT: 5d4bfc8
OBSERVATIONS: Implemented full CRUD operations for city management via REST API. Key challenges encountered and resolved: (1) URL routing issue where the DRF router pattern concatenation caused 404 errors on detail endpoints - fixed by replacing DefaultRouter with explicit path definitions for list and detail views. (2) Django test client API calls returning 404 for cities created via direct ORM - resolved by creating cities via API calls instead of direct database operations, ensuring test database transaction visibility. (3) Paginated list responses required updating step assertions to handle both single object and paginated results. The implementation includes: create/read/update/delete operations, search by name, and a 5-city maximum limit enforcement. All 7 scenarios pass covering city CRUD, search, and limit validation. Step definitions reuse authentication steps from Feature 001.
# End of ENTRY 003

# Start of ENTRY 004
DATE: 2026-01-31 07:13:44
TITLE: Implement Feature 003: Weather Forecast
COMMIT: 2717f5b
OBSERVATIONS: Successfully implemented weather forecast API endpoint for cities. The implementation includes a WeatherForecast model with temperature, humidity, wind speed, and condition fields. The API endpoint at /api/cities/{uuid}/forecast supports an optional 'days' query parameter (max 7 days). When no forecast data exists in the database, mock forecast data is generated dynamically. All 4 scenarios pass: basic forecast retrieval, 7-day limit validation, rejection of requests exceeding 7 days, and verification of weather indicator fields. The migration was initially missing, which caused test failures during database serialization—resolved by running makemigrations.
# End of ENTRY 004

# Start of ENTRY 005
DATE: 2026-01-31 07:22:00
TITLE: Implement Feature 004: Weather Historical Data
COMMIT: df318c84cbea0082d3ff0b2d5d00ea1ebb701438
OBSERVATIONS: Successfully implemented historical weather data API endpoint. Created a new 'historical' Django app with WeatherHistory model mirroring the forecast structure (temperature, humidity, wind_speed, condition fields) but for past dates. The API supports POST to create historical records and GET with a date query parameter to retrieve specific date's data. Fixed a missing JWT authentication step in the feature Background section - the original feature file did not include token acquisition which caused 401 errors when trying to create cities in test setup. Step definitions follow the established pattern from forecast_steps.py. All 3 scenarios pass: retrieving historical data, verifying weather indicators in response, and returning 404 for non-existent data. The historical app is registered in INSTALLED_APPS and URLs are integrated via /api/cities/{uuid}/historical endpoint.
# End of ENTRY 005

# Start of ENTRY 006
DATE: 2026-01-31 07:30:00
TITLE: Implement Feature 005: User Roles and Permissions
COMMIT: d135d3b20ecaaa2e1ac4da1fa17deb1585843422
OBSERVATIONS: Successfully implemented user role-based permissions for the city management API. The permission logic was already present in the cities/views.py from earlier features (using is_staff checks in perform_create, perform_update, perform_destroy). The main work involved fixing test infrastructure issues: (1) The step definition for obtaining JWT tokens was using a hardcoded 'password' for non-admin users instead of the password specified in the feature scenarios (e.g., "viewer123"). Fixed by storing passwords in context.user_passwords dictionary when creating regular users. (2) The "a city exists in the system" step was using the current user's token which would fail when the current user was a regular user without create permissions. Fixed by implementing get_admin_token() helper that temporarily obtains an admin token for setup operations while preserving the original user's token. All 7 scenarios pass: admin can create/update/delete cities, regular user is denied (403) for create/update/delete, and regular user can view cities (200).
# End of ENTRY 006

# Start of ENTRY 007
DATE: 2026-01-31 07:37:00
TITLE: Implement Feature 006: REST API Weather Indicators
COMMIT: 238e437
OBSERVATIONS: Successfully implemented current weather indicators REST API endpoint. Created a new 'weather' Django app with CurrentWeather model containing common weather indicators: temperature (Celsius), humidity (percentage), wind_speed (m/s), pressure (hPa), condition_code, and condition description. The API endpoint at /api/cities/{uuid}/weather supports both GET (retrieve latest weather) and POST (create weather data for testing). Key implementation details: (1) The feature file was missing JWT authentication in the Background section (unlike other features), which caused 401 errors during tests. Fixed by adding the authentication step consistent with Features 003-005. (2) The serializer uses a nested city_uuid field for the response while accepting city_uuid in the create serializer. All 4 scenarios pass: retrieving weather indicators, verifying timestamp field, verifying city UUID association, and returning 404 for non-existent cities. The weather app follows the established patterns from historical and forecast apps.
# End of ENTRY 007

# Start of ENTRY 008
DATE: 2026-01-31 07:42:49
TITLE: Generate features from REQUIREMENTS.md
COMMIT: b12f606
OBSERVATIONS: Added four new feature files (007-010) to complete coverage of all functional requirements from REQUIREMENTS.md. Feature 007 (GraphQL Weather API) enables flexible data querying with support for cities, current weather, forecasts, and historical data queries. Feature 008 (GitHub Webhooks) covers webhook signature validation and event logging for push and pull request events. Feature 009 (Atom Weather Feed) provides RSS/Atom feed format for weather forecasts with proper XML structure and metadata. Feature 010 (WebSocket Weather Alerts) enables real-time weather alert notifications with connection management and alert content validation. All feature scenarios are concrete with specific HTTP status codes and response validations. The features follow BDD best practices with clear Given/When/Then steps.
# End of ENTRY 008

# Start of ENTRY 009
DATE: 2026-01-31 07:59:06
TITLE: Implement Feature 007: GraphQL Weather API
COMMIT: 285f4e4e6aaeccf9bb24655a8b8a6bf93cfb51cf
OBSERVATIONS: Successfully implemented GraphQL API using graphene-django library. The implementation provides a complete GraphQL schema with types for City, CurrentWeather, WeatherForecast, and WeatherHistory models. Key features include: allCities query for listing all cities, city query by UUID, currentWeather query by city UUID, forecast query (limited to 7 days), and historicalWeather query by city and date. Introspection is supported for schema discovery. All 6 GraphQL scenarios pass. The view handles JWT authentication for secured endpoints while allowing unauthenticated introspection queries. Step definitions follow the existing pattern with helper functions for query execution.
# End of ENTRY 009

# Start of ENTRY 010
DATE: 2026-01-31 08:10:00
TITLE: Implement Feature 008: GitHub Webhooks Integration
COMMIT: 0371485
OBSERVATIONS: Successfully implemented GitHub webhooks integration with HMAC SHA256 signature verification. Created a new 'webhooks' Django app with WebhookEvent model to store received events (event_type, delivery_id, payload, timestamp). The webhook endpoint at /api/webhooks/github accepts POST requests from GitHub, validates the X-Hub-Signature-256 header against a configurable secret (GITHUB_WEBHOOK_SECRET env var, defaults to 'test-webhook-secret'), and logs valid events to the database. Invalid signatures return 401. A separate authenticated endpoint at /api/webhooks/github/events allows listing received webhook events. The X-GitHub-Hook-Processed response header is included for successful requests. All 5 scenarios pass: receiving push events with valid signatures, rejecting invalid signatures, receiving pull request events, listing webhook events, and verifying response headers. Step definitions use Python's hmac and hashlib modules to generate test signatures.
# End of ENTRY 010

# Start of ENTRY 011
DATE: 2026-01-31 12:40:53
TITLE: Implement Feature 009: Weather Forecast Atom Feed
COMMIT: ae3313d58836e2af5fa74cbec66edc7f11a25bac
OBSERVATIONS: Successfully implemented Atom feed support for weather forecasts. Created a new 'feeds' Django app with a WeatherAtomFeedView that generates RFC 4287 compliant Atom XML feeds. The feed endpoint at /feeds/{city_uuid}/feed.atom returns weather forecast data in XML format with proper namespace declarations, feed metadata (title, id, updated timestamp, author), and individual entries for each forecast day. Each entry contains temperature, humidity, wind speed, and condition information in both the title summary and detailed HTML content. The implementation uses Python's xml.etree.ElementTree for XML generation. Fixed a URL routing issue where the feeds app had a leading slash in the path pattern which caused 404 errors. Step definitions include XML parsing and validation for feed structure, entry content, and unique identifiers. All 5 scenarios pass: retrieving Atom feed with correct content type, verifying forecast entries exist, validating feed metadata, checking entry uniqueness, and returning 404 for non-existent cities.
# End of ENTRY 011

# Start of ENTRY 012
DATE: 2026-01-31 12:55:00
TITLE: Implement Feature 010: WebSocket Weather Alerts
COMMIT: b547b912c4732ee6abf5cc546f4af1ed72989a46
OBSERVATIONS: Successfully implemented WebSocket weather alerts using Django Channels. Created a new 'alerts' Django app with WeatherAlert model (severity levels: low/moderate/high/severe/extreme, description, timestamp, city reference) and WebSocket consumer at /ws/alerts/{city_uuid}. The implementation uses InMemoryChannelLayer for message broadcasting between clients subscribed to the same city. Key challenges resolved: (1) Async event loop management in behave tests - initial attempts using async_to_sync caused event loop closure errors. Fixed by implementing a shared event loop per scenario (get_event_loop helper) that persists across all async operations within a scenario. (2) WebSocket connection rejection for non-existent cities uses custom close code 4004. Added ASGI configuration (config/asgi.py) with ProtocolTypeRouter for HTTP and WebSocket protocols. Added channels==4.0.0 and daphne==4.1.0 to requirements. All 5 scenarios pass: establishing WebSocket connections, receiving alert messages with severity/description/timestamp, verifying city info in alerts, graceful disconnection, and connection rejection for invalid cities. This completes all 10 features covering the full Weather Forecast Service requirements.
# End of ENTRY 012
