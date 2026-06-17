# Django Project Template

A minimal Django project template with built-in support for HTMX and dependency management powered by UV.

This template is intended to provide a clean starting point for building modern server-rendered web applications using:

- Django
- HTMX
- UV
- Reusable app structure
- Environment-based settings
- Development-ready configuration

## Features

- Django project preconfigured
- HTMX integration out of the box
- Dependency and virtual environment management with UV
- Static and template directories configured
- Environment variable support
- Development-friendly settings
- Ready for PostgreSQL or SQLite
- Simple and extensible structure

## Stack

- Python 3.14+
- Django 6.0
- HTMX
- UV

## Requirements

Install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Documentation:
https://docs.astral.sh/uv/

## Getting Started

### Clone the repository

```bash
git clone git@github.com:retriever-laboratories/django-project-template.git
cd django-project-template
```

### Install dependencies

```bash
uv sync
```

### Apply migrations

```bash
uv run python manage.py migrate
```

### Run the development server

```bash
uv run python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

## Project Structure

```text
django-project-template/
├── LICENSE
├── README.md
├── pyproject.toml
├── src
│   ├── manage.py
│   ├── core
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   └── js/
│   │       └── htmx-init.js
│   └── templates
│       ├── base.html
│       ├── components/
│       └── partials/
└── uv.lock
```

## Development

Create a new app:

```bash
uv run python manage.py startapp myapp
```

Add a new dependency:

```bash
uv add package-name
```

Collect static files:

```bash
uv run python manage.py collectstatic
```

## Docker

The `Dockerfile` builds the Django application image. The image expects a
`DATABASE_URL` environment variable, so production can run the container against
an external database supplied by your hosting or database provider.

`docker-compose.yml` is intended for local development and internal testing. It
starts both the Django application and a local PostgreSQL container. The local
database connection is configured in `.env`:

```env
DATABASE_URL=postgres://django:django@postgres:5432/django_project
```

After changing Python dependencies, regenerate the lockfile before building the
image:

```bash
uv lock
```

### Local Keycloak provider

`docker-compose.yml` also includes a local Keycloak identity provider for
development. It imports `keycloak/import/local-realm.json` on first startup,
which creates:

- Realm: `local`
- SAML client: `django-saml`
- Test user: `testuser`
- Test password: `testpassword`

Start the stack:

```bash
docker compose up keycloak
```

Open the Keycloak admin console:

```text
http://localhost:8080
```

Default admin credentials are configured through `.env`:

```env
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

SAML IdP metadata URL:

```text
http://localhost:8080/realms/local/protocol/saml/descriptor
```

The Django app uses SAML login through `/saml2/login/` and protects views with
`LoginRequiredMiddleware`. In Docker Compose, Caddy serves the app at
`https://localhost`. The local service provider entity ID is `django-saml`, and
the service provider metadata endpoint is:

```text
https://localhost/saml2/metadata/
```

For Docker Compose, keep these values in `.env`:

```env
KEYCLOAK_REALM=local
KEYCLOAK_SAML_CLIENT_ID=django-saml
KEYCLOAK_PUBLIC_BASE_URL=http://localhost:8080
KEYCLOAK_SAML_IDP_METADATA_URL=http://keycloak:8080/realms/local/protocol/saml/descriptor
SAML_SP_ENTITY_ID=django-saml
SAML_SP_ACS_URL=https://localhost/saml2/acs/
SAML_SP_SLO_URL=https://localhost/saml2/ls/
SAML_XMLSEC_BINARY=/usr/bin/xmlsec1
```

`xmlsec1` is installed inside the Django Docker image; it does not need to be
installed on the host machine.

## License

MIT License.
