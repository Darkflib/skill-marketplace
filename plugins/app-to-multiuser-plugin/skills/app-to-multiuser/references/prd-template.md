# PRD Template

Fill every section. Do not leave placeholders — an AI coding agent reading this
must be able to implement without asking clarifying questions (except those
explicitly listed in Open Questions).

---

```markdown
# PRD: <AppName> — Multi-User Web Application

**Version:** 1.0
**Status:** Draft | Review | Approved
**Original app:** <name and brief description>
**Target stack:** Python/FastAPI, React/Vite/Tailwind, Postgres, Redis, RabbitMQ
**ADR index:** ADR-001 through ADR-00N (see `/adrs/`)

---

## 1. Product Overview

### 1.1 Purpose

<What is this product? What does it do? Why is it being built as a multi-user
web app rather than staying single-user? 1-3 paragraphs.>

### 1.2 Success Criteria

- [ ] Users can register/log in via SSO
- [ ] All features of the original app are available via the web UI
- [ ] Data is isolated per tenant
- [ ] <feature-specific criteria>
- [ ] P95 API response time < 200ms for read operations
- [ ] Audit log of all data mutations

### 1.3 Non-Goals (this version)

- <List explicitly what is out of scope>
- Mobile native apps
- Offline mode
- <anything removed from original that isn't being ported>

---

## 2. User Roles

| Role | Description | Key permissions |
|---|---|---|
| Admin | Manages tenant, users, settings | Full CRUD, user management, billing |
| Member | Standard user | Create/edit/delete own resources, view shared |
| Viewer | Read-only access | View only, no mutations |

<Add or remove roles as needed. Derive from the original app's implicit user model.>

---

## 3. Functional Requirements

### 3.1 Authentication & Onboarding

- **FR-AUTH-001**: Users authenticate via OIDC/SSO. No password fields in the app.
- **FR-AUTH-002**: On first login, a tenant is created if the user's `hd` claim
  is not already associated with a tenant. (Or: invite-only onboarding — specify.)
- **FR-AUTH-003**: Users with the Admin role can invite additional users via email.
- **FR-AUTH-004**: Sessions expire after [X] minutes of inactivity. Token refresh
  is handled silently by the React client.

### 3.2 <Feature Group 1 — derived from screen inventory>

<For each screen/feature in the original app, write FR entries in this form:>

- **FR-[GROUP]-NNN**: <Plain-English statement of the requirement. Include:
  who can do it (role), what the action is, what the system does, what feedback
  is given, what edge cases to handle.>

Example:
- **FR-PROJ-001**: An authenticated Member can create a new Project by providing
  a name (required, max 100 chars) and optional description. The system persists
  the project scoped to the current tenant and redirects to the project detail view.
  Duplicate names within a tenant return a 409 with a descriptive error.

### 3.3 <Feature Group 2>

...

### 3.4 Notifications and Real-Time Updates

<If the original app had any live-updating UI, specify the replacement here.>

- **FR-RT-001**: <Describe SSE or WebSocket requirement if needed>

---

## 4. Non-Functional Requirements

### 4.1 Security

- All endpoints require a valid JWT except `/health` and OIDC callback
- All data queries are scoped by `tenant_id` extracted from the JWT
- HTTPS enforced; no HTTP in production
- OWASP Top 10 mitigations applied
- Secrets via environment variables; no secrets in version control
- Structured audit log: `{timestamp, tenant_id, user_id, action, resource_type, resource_id, ip}`

### 4.2 Performance

- P95 read latency: < 200ms
- P95 write latency: < 300ms
- Background jobs: 95th percentile completion within [X] minutes
- API must handle [N] concurrent tenants at expected load

### 4.3 Observability

- Structured JSON logs via `structlog` (level, timestamp, trace_id, tenant_id, user_id)
- `GET /health` returns `{"status": "ok", "db": "ok", "redis": "ok", "queue": "ok"}`
- `GET /metrics` (Prometheus format) — request count, latency histograms, error rates

### 4.4 Deployment

- Docker Compose for local development
- <Target prod environment — fill from user's known infrastructure>
- Alembic migrations run as init container before app starts
- Environment variables documented in `.env.example`

---

## 5. Data Model

### 5.1 Core Entities

<Describe each entity. Include key fields, constraints, relationships.
Derive from the recon report's data model section.>

**Tenant**
- `id: UUID PK`
- `name: str`
- `created_at: datetime`

**User**
- `id: UUID PK` (matches IdP `sub` claim)
- `tenant_id: UUID FK → Tenant`
- `email: str`
- `role: enum(admin, member, viewer)`
- `created_at: datetime`

**<Entity from original app>**
- `id: UUID PK`
- `tenant_id: UUID FK → Tenant`
- `owner_id: UUID FK → User`
- <other fields from recon>
- `created_at: datetime`
- `updated_at: datetime`

### 5.2 Tenancy Boundaries

All tables except `tenants` and `users` have `tenant_id NOT NULL`.
Cross-tenant queries are Admin-only and explicit (no implicit cross-tenant reads).

---

## 6. API Surface

<Not full OpenAPI — just resource groups and operations. The coding agent will
expand to full OpenAPI from this.>

### Auth
- `GET /auth/login` — redirect to IdP
- `GET /auth/callback` — OIDC callback, exchange code for tokens
- `POST /auth/logout` — clear session
- `GET /auth/me` — return current user info

### <Resource 1>
- `GET /<resources>` — list (tenant-scoped, paginated)
- `POST /<resources>` — create
- `GET /<resources>/{id}` — get by ID
- `PATCH /<resources>/{id}` — partial update
- `DELETE /<resources>/{id}` — soft delete (or hard delete — specify)

### Jobs (if background work needed)
- `GET /jobs/{id}` — get job status
- `GET /jobs/{id}/stream` — SSE stream for progress

---

## 7. Implementation Phases

Each phase is a complete, deployable increment. The coding agent implements
phases in order. Each phase ends with passing tests and a green CI pipeline.

### Phase 1: Skeleton
- Project bootstrap via `copier-bootstrap` (fastapi-service template)
- Docker Compose: app, postgres, redis, rabbitmq, keycloak (dev IdP)
- OIDC auth middleware wired up; `GET /auth/me` returns current user
- `GET /health` returns all subsystem statuses
- Alembic baseline migration with `tenants` and `users` tables
- CI pipeline: ruff, mypy, pytest (empty test suite passes)

### Phase 2: Core Data Model + API
- All SQLAlchemy models from data model section
- Alembic migration for all models
- Repository layer with `tenant_id` enforcement
- CRUD endpoints for all resources (no frontend yet)
- Pytest tests: at least happy-path + auth-required + wrong-tenant for each resource

### Phase 3: Frontend Scaffold
- Vite + React + Tailwind + shadcn/ui bootstrap
- OIDC login/logout flow
- Authenticated layout with nav
- TanStack Query setup
- `<Resource>List` and `<Resource>Detail` pages (data from Phase 2 API)

### Phase 4: Feature Parity
- All FR entries from Section 3 implemented
- All screens from original app's screen inventory replicated in React
- End-to-end tests covering core user journeys

### Phase 5: Multi-User Features
- User invitation flow (Admin)
- Sharing / permissions within tenant (if required by FRs)
- Notifications / real-time updates (if required by FRs)
- Audit log viewer (Admin)

---

## 8. Out of Scope

- Mobile native apps
- Billing / payment integration
- Data export (CSV/PDF) — future phase
- <List anything explicitly not being built>

---

## 9. Open Questions

<List decisions that require human input before the agent can implement.
Each question should be specific and actionable.>

1. **IdP selection**: Which OIDC provider will be used in production?
   (Keycloak self-hosted / Auth0 / Okta / Entra) — affects `OIDC_DISCOVERY_URL`
   and client SDK choice.

2. **Tenancy model**: Should tenant creation be self-service on first login,
   or invite-only with a pre-created tenant list?

3. **Data retention**: Are soft deletes required, or is hard delete acceptable?

4. <Add app-specific questions from recon unknowns>

---

## Appendix A: Screen Inventory

<Copy from recon report — screen name, purpose, key data, key actions>

## Appendix B: Original Dependency Map

<Copy from recon report>

## Appendix C: Single-User Assumption Inventory

<Copy from Phase 2 analysis — the full table with change required + complexity>
```
