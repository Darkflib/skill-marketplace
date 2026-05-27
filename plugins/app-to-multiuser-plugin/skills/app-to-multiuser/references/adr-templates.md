# ADR Templates

Use this format for all ADRs. Number sequentially: ADR-001, ADR-002, etc.
Keep each ADR focused on a single decision. Cross-reference related ADRs.

---

## Base Template

```markdown
# ADR-NNN: <Decision Title>

**Status:** Proposed | Accepted | Superseded by ADR-XXX
**Date:** YYYY-MM-DD
**Deciders:** [list if known]

## Context

<What situation in the original app prompted this decision? What constraint or
requirement in the multi-user version makes this non-trivial? 2-4 sentences.>

## Decision

<The decision, stated plainly. "We will use X for Y.">

## Rationale

<Why this option. Link to stack-defaults.md if this is a default choice.>

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| ... | ... | ... | ... |

## Consequences

**Positive:**
- ...

**Negative / Trade-offs:**
- ...

**Risks:**
- ...

## Implementation Notes

<Specific implementation guidance for the coding agent. Package names, config
patterns, gotchas. Keep this actionable.>
```

---

## Pre-filled ADR Stubs

Copy, fill in context-specific detail, and adjust as needed.

---

### ADR-001: Authentication Mechanism

```markdown
# ADR-001: Authentication Mechanism

**Status:** Accepted

## Context

The original app had no authentication — it ran as a single user on a local machine.
The multi-user version requires identity, session management, and the ability to
scope data per user/tenant.

## Decision

We will use OIDC/SSO via an external Identity Provider (IdP). The API validates
JWT access tokens (RS256) on every request. No local password storage.

## Rationale

SSO offloads credential management and MFA to a dedicated system. OIDC is the
industry standard for this pattern. Authlib provides a mature FastAPI integration.

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| Username + password (bcrypt) | Self-contained | Password storage, MFA complexity | Added attack surface |
| API key only | Simple | No user identity, no SSO | Doesn't support end-user sessions |
| Magic link / passwordless | Good UX | Email dependency, more complex | Overkill for phase 1 |

## Consequences

**Positive:**
- No password storage in our DB
- MFA, audit logging, group management delegated to IdP
- Standard JWT allows stateless verification

**Negative / Trade-offs:**
- Requires an IdP to be running (local dev: Keycloak in Docker Compose)
- Token expiry and refresh handling required in the React client

## Implementation Notes

- Use `authlib` for OIDC discovery and JWT validation
- FastAPI dependency: `get_current_user(token: str = Depends(oauth2_scheme))`
- Decode token: `authlib.jose.jwt.decode(token, jwks)`
- Extract: `sub` (user ID), `email`, `groups` (for RBAC)
- Local dev: Keycloak in Docker Compose; set `OIDC_DISCOVERY_URL` in `.env`
- Do not hardcode JWKS — fetch from discovery endpoint on startup, cache with TTL
```

---

### ADR-002: Database

```markdown
# ADR-002: Database

**Status:** Accepted

## Context

The original app persisted data to [FILL: local SQLite file / electron-store /
flat files / etc.]. The multi-user version needs shared, concurrent-safe storage
with per-tenant data isolation.

## Decision

SQLAlchemy 2.x (async) as the ORM. SQLite for local development.
PostgreSQL 16+ for staging and production. Schema managed by Alembic.

## Rationale

Single ORM, two DB backends via config. Dev can run with zero infrastructure.
Prod gets a production-grade database. SQLAlchemy async models are compatible
with both backends. Alembic provides reproducible schema migrations.

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| Prisma (Python) | Type-safe | Immature Python support | Ecosystem risk |
| Tortoise ORM | Async-first | Smaller community | Prefer SQLAlchemy |
| Raw asyncpg | Maximum control | No abstraction | Dev/prod parity harder |

## Consequences

**Positive:**
- Zero-config dev environment (SQLite)
- Production-ready (Postgres)
- Alembic migration history in version control

**Negative / Trade-offs:**
- SQLite and Postgres have subtle SQL differences — test against Postgres in CI
- Async SQLAlchemy session management requires careful context handling

## Implementation Notes

- `DATABASE_URL=sqlite+aiosqlite:///./dev.db` (dev)
- `DATABASE_URL=postgresql+asyncpg://...` (prod)
- Session factory via `async_sessionmaker`; inject as FastAPI dependency
- All models inherit from `Base` with `tenant_id: Mapped[UUID]` column
- Alembic `env.py` must import all models for autogenerate to work
- Run `alembic upgrade head` in a k8s init container or Compose `depends_on` hook
```

---

### ADR-003: Session State and Caching

```markdown
# ADR-003: Session State and Caching

**Status:** Accepted

## Context

The original app held UI state in-process (Redux store / module globals / etc.).
The multi-user version needs state that survives across requests and can be shared
across multiple API instances.

## Decision

Redis 7+ for all server-side session state and hot-path caching.
JWTs are stateless — no server-side session record needed for auth.
Redis is used for: rate limiting, short-lived operation state, pub/sub for
real-time features, and caching expensive queries.

## Rationale

Redis is already in the stack for RabbitMQ adjacency. Stateless JWTs keep the
API horizontally scalable. Redis TTL handles expiry automatically.

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| DB-backed sessions | Durable | Slower, adds DB load | Redis is faster for hot state |
| In-memory (single instance) | Simple | Not horizontally scalable | Breaks multi-replica deploy |
| Memcached | Fast | No pub/sub, no persistence | Redis is a superset |

## Implementation Notes

- `redis-py` async client: `redis.asyncio.from_url(settings.REDIS_URL)`
- Key namespacing: `{tenant_id}:{resource}:{id}` — never unnamespaced keys
- Default TTL: 15 minutes for operation state, 5 minutes for cached queries
- Pub/sub channel pattern: `{tenant_id}.events.{resource}` for real-time push
```

---

### ADR-004: Multi-Tenancy Model

```markdown
# ADR-004: Multi-Tenancy Model

**Status:** Accepted

## Context

The original app had no tenancy concept. The multi-user version must isolate
data between organisations/teams while allowing users within a tenant to share data.

## Decision

Row-level tenancy: all tables have a `tenant_id UUID NOT NULL` column.
All queries are scoped by `tenant_id` at the repository layer.
Single shared schema, single database.

## Rationale

Row-level tenancy is the simplest model that works for most B2B SaaS apps.
It supports a shared infrastructure cost model and is easy to reason about.
Schema-per-tenant and DB-per-tenant are reserved for regulated industries or
customers requiring hard data isolation (future ADR if needed).

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| Schema-per-tenant | Hard isolation | Migration complexity, connection pool pressure | Overkill for phase 1 |
| DB-per-tenant | Maximum isolation | Operational complexity | Reserve for enterprise tier |

## Consequences

**Positive:**
- Simple to implement and query
- Easy cross-tenant analytics (admin queries)

**Negative / Trade-offs:**
- Must enforce `tenant_id` filter consistently — a missing filter leaks data
- Harder to export/delete a single tenant's data at DB level

## Implementation Notes

- Base SQLAlchemy model: `tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)`
- Repository base class enforces `WHERE tenant_id = :tenant_id` on all queries
- `get_current_tenant()` FastAPI dependency extracts `tenant_id` from JWT claim
- Add a Postgres row-security policy as a defence-in-depth measure (optional but recommended)
```

---

### ADR-005: Background Work

```markdown
# ADR-005: Background Work

**Status:** Accepted | Only required if original app had long-running operations

## Context

The original app performed [FILL: file processing / report generation / data import /
etc.] as blocking operations in the main process. In a multi-user API, blocking
requests beyond ~500ms degrades the user experience and ties up server resources.

## Decision

Long-running operations are dispatched as CloudEvents messages to a RabbitMQ topic
exchange. Dedicated async worker processes consume from queue and report progress
via Redis pub/sub. The API returns a `202 Accepted` with a job ID immediately.

## Rationale

Decouples request latency from operation duration. Workers scale independently.
CloudEvents provides a standard envelope for message routing and observability.
Matches the existing infrastructure stack.

## Alternatives Considered

| Option | Pros | Cons | Rejected because |
|---|---|---|---|
| Celery | Mature | Heavy, pip-only, implicit magic | Not in stack |
| FastAPI BackgroundTasks | Simple | In-process, no persistence, no retry | Not durable |
| `asyncio.create_task` | Simple | Same as above | Not durable |

## Implementation Notes

- Exchange: `app.work` (topic), durable
- Routing key: `{tenant_id}.{operation_type}`
- Message envelope: CloudEvents 1.0 JSON
- Worker: `aio-pika` consumer, `async for message in queue`
- Progress channel: Redis pub/sub `{tenant_id}.jobs.{job_id}`
- Frontend polls or subscribes via SSE endpoint `/jobs/{job_id}/stream`
```

---

### ADR-006: File Storage (if applicable)

```markdown
# ADR-006: File Storage

**Status:** Accepted | Only required if original app read/wrote local files

## Context

The original app read/wrote files from the local filesystem [FILL: describe what].
In a multi-user deployment, local filesystem access is ephemeral and not shared
across instances.

## Decision

Files are stored in object storage (GCS or S3). The API generates pre-signed URLs
for direct client upload/download. File metadata is stored in Postgres.

## Implementation Notes

- `google-cloud-storage` (GCS) or `boto3` (S3)
- Bucket structure: `{bucket}/{tenant_id}/{resource_type}/{uuid}/{filename}`
- Metadata table: `files(id, tenant_id, resource_id, resource_type, bucket, key, content_type, size, created_at)`
- Pre-signed upload URL TTL: 15 minutes
- Pre-signed download URL TTL: 1 hour (or stream via API if access control required)
```
