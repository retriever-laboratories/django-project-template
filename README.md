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

### SAML identity provider

The Django app is configured as a generic SAML service provider. Projects built
from this template should point the app at their external identity provider by
setting `SAML_IDP_METADATA_URL` and the public application URL in
`APP_BASE_URL`. The service provider SAML URLs are derived from
`APP_BASE_URL`.

`docker-compose.yml` includes Keycloak only as a local development identity
provider. Its local-only configuration is hardcoded in Compose and in
`keycloak/import/local-realm.json`, so application environments do not need
Keycloak-specific variables. The imported realm creates:

- Realm: `local`
- SAML client: `django-saml`
- Test user: `testuser`
- Test password: `testpassword`

Start the local IdP:

```bash
docker compose up keycloak
```

Open the Keycloak admin console:

```text
http://localhost:8080
```

Default local admin credentials are `admin` / `admin`.

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

For Docker Compose local development, keep these values in `.env`:

```env
APP_BASE_URL=https://localhost
SAML_IDP_METADATA_URL=http://keycloak:8080/realms/local/protocol/saml/descriptor
SAML_SP_ENTITY_ID=django-saml
SAML_SESSION_COOKIE_SAMESITE=None
```

`xmlsec1` is installed inside the Django Docker image; it does not need to be
installed on the host machine.

For production or shared environments, replace the app URL and external IdP
metadata URL:

```env
APP_BASE_URL=https://app.example.com
SAML_IDP_METADATA_URL=https://idp.example.com/metadata
SAML_SP_ENTITY_ID=django-saml
```

For Okta-style SAML applications, map the fields this way:

- Entity ID: `SAML_SP_ENTITY_ID`
- Single sign-on URL, Recipient, and Destination: `{APP_BASE_URL}/saml2/acs/`
- Default RelayState: blank unless the app has a specific landing path
- Name ID format: `Unspecified`
- Application username: usually Okta username or email, depending on the user key

The service provider always requests the `unspecified` NameID format because
that is the enterprise SAML convention this template targets.

## License

MIT License.
