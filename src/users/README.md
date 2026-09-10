# Users and OIDC

After adding these dependencies, run `uv lock` and `uv sync`, then
`uv run python src/manage.py test users`. The lockfile must be regenerated
before the Docker image's `uv sync --frozen` step can include Authlib.

`User` extends Django's `AbstractUser`. `subject` identifies the user at our
single configured OIDC provider. The inherited `groups` relationship stores
membership in Django permission groups, synchronized by name from OIDC.
New groups have no permissions until configured. Membership grants the group's
configured permissions, but does not set staff or superuser status.

Configure `OIDC_PROVIDER_DOMAIN`, `OIDC_CLIENT_ID`, and `OIDC_CLIENT_SECRET` for
an Auth0 Regular Web Application. Set the domain to `your-tenant.auth0.com`
without a scheme or path. The client builds `https://your-tenant.auth0.com/`
automatically for issuer validation, discovery, and logout.
`OIDC_AUDIENCE` is optional.

The **ID token** is expected to contain an array of strings under the claim key
configured by `OIDC_GROUPS_CLAIM` (default: `groups`). For a namespaced claim,
set it to the exact key, such as `https://your-app.example/groups`.
Each name is resolved to a Django `Group`, creating it if needed, and
`user.groups.set()` replaces memberships. A missing claim clears memberships.
OIDC is authoritative: manually assigned memberships are replaced on login.
The client requests `openid profile email groups`. Configure the provider to
emit the groups claim; requesting the scope alone does not populate it.
See [Auth0 custom claims](https://auth0.com/docs/secure/tokens/json-web-tokens/create-custom-claims).

`OIDCClient.authorize_redirect(request, redirect_uri)` starts login.
`OIDCClient.authenticate(request)` handles the callback and returns the local
user after Authlib validates the ID token. The callback view starts the Django
session. `core.urls` includes the following routes from `users.urls`:

- `GET /login/`: starts OIDC login, with an optional same-host `next` URL.
- `GET /login/callback/`: validates the response and logs the user into Django.
- `POST /logout/`: clears the Django session and redirects the browser to
  Auth0's `/v2/logout`; submit with a CSRF token.

Register the full `/login/callback/` URL in Auth0's Allowed Callback URLs.
Login and logout redirect to `/` by default. Add the absolute logout return URL
(for example, `https://your-app.example/`) to the Auth0 application's **Allowed
Logout URLs**. Auth0 clears its browser session before returning there.
`OIDCAdminMiddleware` protects `/admin/` and its subroutes, including the admin
login form. Anonymous users redirect to OIDC login. Authenticated users need
an external identity and a group in `OIDC_ADMIN_GROUPS`; otherwise access is
denied with 403. An empty allowed-group list denies access. Django still applies
its staff and permission checks after this gate; local superusers do not bypass it.

## Login required by default

### Optional custom admin site

`users.admin_site.OIDCAdminSite` implements the admin group gate through
`has_permission()` and `login()`. To activate it, replace `django.contrib.admin`
in `INSTALLED_APPS` with `users.apps.Admin`, then remove
`users.middleware.OIDCAdminMiddleware` from `MIDDLEWARE`. The existing
`admin.site.urls` route and model registrations stay unchanged. The configuration
is provided but not enabled; the middleware continues protecting admin until
you make this replacement.

Django's `LoginRequiredMiddleware` runs after `AuthenticationMiddleware`.
Unauthenticated requests redirect to `/login/?next=...`. Our public views use
`@login_not_required`: `/login/`, `/login/callback/`, `/logout/`, and `/health/`.
Logout still requires POST and CSRF protection. Other application views require
a Django session. To make another view public, apply `@login_not_required` from
`django.contrib.auth.decorators`.

Django's admin login has its own public exemption from `LoginRequiredMiddleware`,
but the separate `OIDCAdminMiddleware` enforces the group gate for it as well.

`OIDCClient._sync_user_from_claims()` accepts only previously validated claims. Users match
by subject, never email. Federated passwords are made unusable at every sync.
Groups are replaced, and missing groups clear prior membership. Successful OIDC
synchronization sets `is_active=True`, including for previously inactive users.
`user_has_admin_group()` checks `OIDC_ADMIN_GROUPS` but does not
replace the admin access gate or Django's permission checks.

The provider is a single configured trust source. Switching providers requires
an identity migration; subjects must not be reassigned to another provider.

For a fresh database, run `uv run python src/manage.py migrate`. If the database
already has Django auth/admin migrations applied, switching `AUTH_USER_MODEL`
requires a planned schema/data migration. Do not delete data or fake migrations
to bypass that requirement. This change does not migrate an existing database.
