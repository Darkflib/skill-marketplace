# C4 Diagram Patterns (Mermaid)

Use these templates for the architecture diagrams in the output bundle.
Mermaid C4 uses `C4Context`, `C4Container`, `C4Component` diagram types.

Only include containers/components that are actually needed for this app.
Don't add Redis if there's no session state or caching requirement.
Don't add RabbitMQ if all operations are synchronous.

---

## Context Diagram Template

```mermaid
C4Context
  title System Context — <AppName> Multi-User

  Person(user, "End User", "Authenticated tenant member using the web app")
  Person(admin, "Tenant Admin", "Manages users, settings, and tenant data")

  System(app, "<AppName>", "Multi-user web application — replaces single-user desktop app")

  System_Ext(idp, "Identity Provider", "OIDC/SSO — Keycloak / Auth0 / Okta / Entra")
  System_Ext(email, "Email Service", "Transactional email — invitations, notifications")

  %% Add other external systems if the original app consumed them:
  %% System_Ext(thirdparty, "Third-Party API", "Description of what it provides")

  Rel(user, app, "Uses", "HTTPS")
  Rel(admin, app, "Administers", "HTTPS")
  Rel(app, idp, "Authenticates via", "OIDC/HTTPS")
  Rel(app, email, "Sends email via", "SMTP/API")
```

---

## Container Diagram Template

```mermaid
C4Container
  title Container Diagram — <AppName> Multi-User

  Person(user, "End User")

  Container_Boundary(frontend, "Frontend") {
    Container(spa, "React SPA", "React 18, Vite, Tailwind, shadcn/ui", "Browser-based UI")
  }

  Container_Boundary(backend, "Backend") {
    Container(api, "FastAPI", "Python 3.12, FastAPI, SQLAlchemy, authlib", "REST API — auth, business logic, data access")
    Container(worker, "Async Worker", "Python 3.12, aio-pika", "Processes background jobs from RabbitMQ")
  }

  Container_Boundary(data, "Data") {
    ContainerDb(db, "PostgreSQL", "PostgreSQL 16", "Primary data store — tenant data, user data")
    ContainerDb(redis, "Redis", "Redis 7", "Session state, caching, pub/sub")
    ContainerDb(mq, "RabbitMQ", "RabbitMQ 3", "Work queue — long-running job dispatch")
  }

  System_Ext(idp, "Identity Provider", "OIDC/SSO")
  System_Ext(storage, "Object Storage", "GCS / S3 — file attachments")  %% remove if not needed

  Rel(user, spa, "Uses", "HTTPS")
  Rel(spa, api, "API calls", "REST/JSON HTTPS")
  Rel(api, idp, "Validates JWT via", "OIDC discovery HTTPS")
  Rel(api, db, "Reads/writes", "asyncpg")
  Rel(api, redis, "Caches / pub-sub", "Redis protocol")
  Rel(api, mq, "Dispatches jobs", "AMQP")
  Rel(worker, mq, "Consumes jobs", "AMQP")
  Rel(worker, db, "Reads/writes", "asyncpg")
  Rel(worker, redis, "Publishes progress", "Redis pub/sub")
  Rel(api, storage, "Pre-signed URLs", "HTTPS")  %% remove if not needed
```

---

## Minimal Container Diagram (no worker, no file storage)

```mermaid
C4Container
  title Container Diagram — <AppName> (Minimal)

  Person(user, "End User")

  Container(spa, "React SPA", "React 18, Vite, Tailwind", "Web UI")
  Container(api, "FastAPI", "Python 3.12, FastAPI", "REST API")
  ContainerDb(db, "PostgreSQL", "PostgreSQL 16", "Primary store")
  ContainerDb(redis, "Redis", "Redis 7", "Session / cache")

  System_Ext(idp, "Identity Provider", "OIDC/SSO")

  Rel(user, spa, "Uses", "HTTPS")
  Rel(spa, api, "API calls", "REST/JSON")
  Rel(api, idp, "Validates JWT", "HTTPS")
  Rel(api, db, "Reads/writes", "asyncpg")
  Rel(api, redis, "Cache", "Redis")
```

---

## BFF Variant (only if ADR mandates BFF)

```mermaid
C4Container
  title Container Diagram — <AppName> with BFF

  Person(user, "End User")

  Container(spa, "React SPA", "React 18, Vite, Tailwind", "Web UI")
  Container(bff, "BFF", "Python 3.12, FastAPI", "UI-optimised API — auth, aggregation")
  Container(api, "Core API", "Python 3.12, FastAPI", "Domain API — business logic, data")
  ContainerDb(db, "PostgreSQL", "PostgreSQL 16", "Primary store")
  ContainerDb(redis, "Redis", "Redis 7", "Session / cache")

  System_Ext(idp, "Identity Provider", "OIDC/SSO")

  Rel(user, spa, "Uses", "HTTPS")
  Rel(spa, bff, "Calls", "REST/JSON HTTPS")
  Rel(bff, idp, "Validates / exchanges tokens", "OIDC HTTPS")
  Rel(bff, api, "Calls", "REST/JSON internal")
  Rel(api, db, "Reads/writes", "asyncpg")
  Rel(api, redis, "Cache", "Redis")
```

---

## Notes on C4 in Mermaid

- `Person` — human users
- `System_Ext` — external systems outside your control
- `Container` — deployable unit (process, service, SPA, DB)
- `ContainerDb` — database / data store container (rendered differently)
- `Container_Boundary` — groups containers logically (optional, cosmetic)
- `Rel(from, to, "label", "technology")` — directed relationship

Keep diagrams honest: only include what is actually in the architecture.
A diagram with 5 real containers is better than one with 10 aspirational ones.
