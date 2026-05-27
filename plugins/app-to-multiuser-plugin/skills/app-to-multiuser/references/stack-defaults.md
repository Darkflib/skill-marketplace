# Stack Defaults

Opinionated defaults for the multi-user target stack. These are starting points —
override via ADR if the app's requirements justify it.

---

## Backend

| Concern | Choice | Notes |
|---|---|---|
| Language | Python 3.12+ | |
| Web framework | FastAPI (async) | `uvicorn` runner, `gunicorn` in prod |
| Package management | `uv` | No pip, no poetry |
| Linting/formatting | `ruff` + `ruff format` | Replace isort, black, flake8 |
| Type checking | `mypy` (strict) | |
| Testing | `pytest` + `pytest-asyncio` + `httpx` | |
| ORM | SQLAlchemy 2.x (async) | Declarative models, Alembic migrations |
| DB (dev) | SQLite (via SQLAlchemy) | Single-file, zero-config |
| DB (prod) | PostgreSQL 16+ | `asyncpg` driver |
| Cache / session state | Redis 7+ | `redis-py` async client |
| Message queue | RabbitMQ 3.x | `aio-pika`; CloudEvents envelope |
| Background workers | Plain asyncio workers consuming RabbitMQ | No Celery |
| Auth | OIDC/SSO via `authlib` | See auth section below |
| Secrets | Environment variables; `python-dotenv` for local dev | |
| Logging | Structured JSON via `structlog` | |
| Config | `pydantic-settings` | |

### Project bootstrap

Use `copier-bootstrap` skill to scaffold. Target template: `fastapi-service`.

```
pyproject.toml   ← uv-managed, ruff + mypy + pytest config here
src/
  <appname>/
    main.py      ← FastAPI app factory
    config.py    ← pydantic-settings Settings
    models/      ← SQLAlchemy models
    schemas/     ← Pydantic v2 request/response schemas
    routers/     ← FastAPI routers, one per resource
    services/    ← business logic, no ORM calls here
    repositories/← all ORM calls here
    workers/     ← RabbitMQ consumers
    auth/        ← OIDC middleware, JWT decode, RBAC helpers
tests/
alembic/
```

---

## Auth

**Default: OIDC/SSO** — assume an external IdP (Keycloak, Auth0, Okta, Entra, etc.)

- FastAPI dependency `get_current_user` decodes and validates JWT (RS256)
- Access token in `Authorization: Bearer` header
- Token claims provide user identity + groups/roles
- Refresh handled client-side (React) or via a thin `/auth/refresh` proxy endpoint
- No local user password storage by default

**Row-level tenancy**: every model gets a `tenant_id` (UUID) FK. All queries scoped
by `tenant_id` extracted from the JWT claim. Enforce at the repository layer, never
the router layer.

**RBAC**: roles from JWT `groups` claim or a local `user_roles` table. Start with
three roles: `admin`, `member`, `viewer`. Define in `auth/roles.py`.

---

## Frontend

| Concern | Choice | Notes |
|---|---|---|
| Framework | React 18+ | |
| Build tool | Vite 5+ | |
| Styling | Tailwind CSS 3+ | |
| Component library | shadcn/ui | Unstyled primitives, copy-paste model |
| State (server) | TanStack Query v5 | Cache, invalidation, optimistic updates |
| State (client) | Zustand | Minimal global state only |
| Routing | React Router v6 | |
| Forms | React Hook Form + Zod | |
| Auth client | `oidc-client-ts` or IdP SDK | |
| HTTP | `axios` or native `fetch` with a typed wrapper | |
| Testing | Vitest + Testing Library | |

### BFF consideration

Don't add a BFF by default. Add it (as a separate FastAPI app or router prefix) if:
- The frontend needs aggregated responses that would require 3+ sequential API calls
- Auth token exchange must be server-side (confidential client requirement)
- The frontend team and API team are separate and need contract isolation

If BFF is added, it sits between React and the core API, handles auth, and exposes
UI-optimised endpoints. It does not own data — it orchestrates.

---

## Infrastructure

| Concern | Choice | Notes |
|---|---|---|
| Container | Docker + Compose (dev), k3s/k8s (prod) | |
| DB migrations | Alembic (`alembic upgrade head` in init container) | |
| Secrets (prod) | GCP Secret Manager via External Secrets Operator | Or Vault |
| Reverse proxy | Caddy or nginx | TLS termination |
| CI | GitHub Actions | `uv run pytest`, ruff, mypy in pipeline |

---

## What to replace

| Single-user mechanism | Multi-user replacement |
|---|---|
| `electron-store` / local JSON | Postgres via SQLAlchemy |
| `localStorage` | Redis (server-side session) or JWT claims |
| Local SQLite file | Postgres (keep SQLite for dev via SQLAlchemy) |
| Local file writes | Object storage (S3/GCS) or DB blob |
| In-process background threads | RabbitMQ worker |
| Hardcoded user paths (`~/`) | Per-tenant storage prefix |
| No auth | OIDC/SSO |
| Global mutable state | DB or Redis, scoped by tenant/user |
