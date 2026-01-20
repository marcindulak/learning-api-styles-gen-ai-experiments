# Weather Forecast Service

Before implementing various web APIs, we need to create a context in which we can use these APIs.
We need an educational application that will encapsulate various APIs into one project.
Without such an application, our web APIs would be loosely hanging code snippets that are hard to relate to.
Therefore we'll design an application--the Weather Forecast Service (WFS)--by translating client needs to domain concepts, and the concepts to the code.
We chose the weather because everyone can intuitively relate to it.

Functional Requirements

| Feature (FR) | Designer's Note |
|--------------|-----------------|
| Service exposes common weather indicators via various web APIs | Research common weather indicators; REST, GraphQL |
| Service integrates with GitHub via webhooks | Webhooks API |
| Service provides weather forecast feed | Atom as API |
| Service provides weather alerts | Websocket API |
| Service provides weather historical data | Model domain |
| Service has a content management system for admin user | Custom CMS? |
| Weather records contain actual data | Find 3rd party weather API |
| Weather data is limited to the 5 biggest cities in the world | What are they? |
| Weather forecast is limited to up to 7 days | Model domain |
| Service has two users: admin, and regular user | Object level permission |

Non-Functional Requirements

| Feature (NFR) | Quality Attribute | Designer's Note |
|---------------|-------------------|-----------------|
| Service operates in a local environment | Portability | Containers |
| Service requests can be encrypted or unencrypted | Security | TLS |
| Service is deployed as one unit | Deployability | Monolith |
| Service is testable | Testability | End-to-end testings, integration testings |
| Service APIs are documented | Documentability | OpenAPI Spec, AsyncAPI Spec |
| Service is runnable by a majority of book readers | Deployability | Containers, GitHub Codespaces |

The first decision is what programming language to use.
We chose Python--one of the most popular programming languages according to https://survey.stackoverflow.co/2023/#most-popular-technologies-language-other[stackoverflow's survey 2023].

The next decision is influenced by the _"Service has a content management system for admin user"_ requirement.
This functional requirement comes as an exception since the section deals with NFRs.
The question to answer was whether to use a framework or not.
We chose the https://www.djangoproject.com/[Django] framework because of its built-in content and user management system.
One of our goals is that the code associated with the book is maintainable for a longer period of time, in addition to the general concepts, which are also expected to be valid during a long time.
Furthermore, Django is actively developed, well supported, has many plugins, and a large community.

We leaned towards using a database to fulfil the _"Service provides weather historical data"_ requirement.
We chose the open-source https://www.postgresql.org/[PostgreSQL] database, due to its popularity and support in Django.

Another decision is driven by the following NFRs:

* Service operates in a local environment.

* Service is runnable by a majority of book readers.

To satisfy these two requirements, we chose https://www.docker.com/[Docker] as a containerization solution, and https://github.com/features/codespaces[GitHub Codespaces] as runtime environment.
Making these decisions, we effectively tackled deployability and portability.
To facilitate the implementation, `Dockerfile` and `compose.yaml` files are already present at the root of the project.

```
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The last requirement described in this section is _"Service is testable"_.
For testing, we chose native to the framework test library, supplemented by https://behave-django.readthedocs.io/en/stable/[django-behave].

Here is how `behave-django` can be used inside of the running container:

```
docker compose exec app python manage.py behave --no-input
```

Additionally, end-to-end tests need to be performed using curl.
Here is an example:

```
# Get JWT access token
CREDENTIALS_PAYLOAD='{"username":"admin","password":"admin"}'
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl \
  --data '$CREDENTIALS_PAYLOAD' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent 'http://localhost:8000/api/jwt/obtain' | \
  jq --raw-output '.access'")

# CREATE: Create a city
CREATE_CITY_PAYLOAD='{"name":"Copenhagen",
  "country":"Denmark",
  "region":"Europe",
  "timezone":"Europe/Copenhagen",
  "latitude":55.676100,
  "longitude":12.568300}'
docker compose exec app bash -c \
       "curl \
       --data '$CREATE_CITY_PAYLOAD' \
       --header 'Authorization: Bearer $ACCESS_TOKEN' \
       --header 'Content-Type: application/json' \
       --request 'POST' \
       --silent \
       'http://localhost:8000/api/cities' | \
       jq"

# READ: Obtain UUID of the city and get the city
CITY_UUID=$(docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search_name=Copenhagen' | \
  jq --raw-output '.results[0].uuid'")
docker compose exec app bash -c \
       "curl \
       --request 'GET' \
       --silent \
       'http://localhost:8000/api/cities/$CITY_UUID' | \
       jq"
```
