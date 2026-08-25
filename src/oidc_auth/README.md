# OIDC Authentication

This app configures a Django monolith to delegate sign-in to an OIDC provider
such as Auth0 or Okta, then stores the authenticated user locally with Django's
built-in `User` model.

## Environment

Set these values in `.env`:

```env
OIDC_PROVIDER_DOMAIN=your-tenant.auth0.com
OIDC_CLIENT_ID=change-me
OIDC_CLIENT_SECRET=change-me
OIDC_AUDIENCE=
OIDC_SCOPES=openid profile email groups
OIDC_GROUPS_CLAIM=groups
OIDC_ADMIN_GROUPS=
LOGIN_REDIRECT_URL=/
LOGOUT_REDIRECT_URL=/
```

Use `OIDC_ISSUER` instead of `OIDC_PROVIDER_DOMAIN` when the issuer URL cannot
be derived as `https://{domain}`.

Set `OIDC_AUDIENCE` to the API/resource identifier when the provider should
issue an access token for that API.

Some providers expose groups in a namespaced claim instead of `groups`. In that
case, set `OIDC_GROUPS_CLAIM` to the exact claim name.

Set `OIDC_ADMIN_GROUPS` to a comma-separated list of OIDC groups that should be
allowed to reach Django admin. The Django admin login form is also behind this
OIDC group gate, so emergency username/password login is only available after an
authorized OIDC user has authenticated.

## Local User Storage

Successful sign-in creates or updates:

- a Django `User`, matched first by OIDC subject and then by email
- a `UserIdentity`, storing the OIDC subject, groups, and raw claims

The integration does not grant Django admin access automatically. To use admin,
the OIDC-authenticated user must also have local Django `is_staff` and any
required permissions.

## Login Requirement

All pages require login by default except:

```text
/login/
/login/callback/
/logout/
/health/
/static/
/media/
```

Override this with `LOGIN_EXEMPT_URLS` if an environment needs additional public
paths.
