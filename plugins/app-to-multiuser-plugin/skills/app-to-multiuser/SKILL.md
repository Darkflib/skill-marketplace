---
name: app-to-multiuser
description: >
  Reverse-engineer a single-user GUI or Electron app and produce a fully-specified
  PRD + ADR package that an AI coding agent (Claude Code, Codex, etc.) can implement
  directly. Use this skill whenever the user wants to convert, port, or re-architect
  a single-user desktop or local GUI app into a networked, multi-user web application.
  Trigger on phrases like "convert this app to multi-user", "make this web-based",
  "port this desktop app", "add multi-user support", "turn this into a SaaS",
  "network-enable this app", or any task involving extracting a spec from an existing
  app codebase. The skill covers recon, assumption inventory, architecture selection,
  C4 diagramming, and generation of PRD + ADR documents ready for agentic implementation.
---

# App → Multi-User Migration Skill

Converts a single-user GUI/Electron app into a fully-specified multi-user web application.
Primary output is a **PRD + ADR bundle** ready for agentic implementation (Claude Code, Codex, etc.).
Code generation is a secondary output — the docs come first.

**Read `references/stack-defaults.md` now** for the opinionated default stack.
Reference other files as needed during the relevant phase.

---

## Workflow Overview

```
Phase 1: RECON          — gather all available evidence about the app
Phase 2: ANALYSIS       — inventory single-user assumptions, data model, state
Phase 3: ARCHITECTURE   — select target patterns, produce C4 diagrams
Phase 4: DECISIONS      — write ADRs for key architectural choices
Phase 5: PRD            — produce the implementation-ready product spec
```

Run phases in order. Each phase gates the next — don't skip recon.

---

## Phase 1: Recon

**This is the most critical phase.** The quality of everything downstream depends on
how thoroughly you understand the existing app. Be aggressive about gathering evidence.

### 1.1 Evidence Sources (use all that are available)

**Screenshots / UI**
- Ask the user for screenshots of every distinct screen, dialog, and state
- If Electron/web, ask them to walk through the app while you observe or they describe
- Catalogue: screens, navigation flows, modals, settings panels, notifications
- Note: what data is displayed, what actions are available, what feedback is given

**Source Code**
- If provided: read entry points, main process (Electron: `main.js`/`main.ts`), renderer
- Map module structure — don't read everything, build a dependency graph first
- Identify: state management (Redux, Zustand, MobX, plain globals, module-level vars)
- Identify: persistence calls (fs, sqlite, localStorage, electron-store, etc.)
- Identify: any existing IPC (Electron) or network calls
- Look for: hardcoded paths, user-home references, single-user shortcuts

**Filesystem Layout**
- Ask for or scan: directory listing, config file locations, data file locations
- Note: where does the app write? (`~/.appname`, `%APPDATA%`, local DB file, etc.)
- Note: what file formats are used for persistence?

**Dependencies / Package Manifests**
- Read `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, etc.
- Flag: UI framework, state library, persistence library, any existing network libs
- Flag: anything that will need replacing (e.g., `electron-store` → Redis/Postgres)

**Runtime Behaviour (if accessible)**
- Ask user to describe or demonstrate: what happens on first launch, on data load,
  on concurrent use attempts (if any), on crash/restart
- Ask: what data persists between sessions? What resets?

### 1.2 Recon Output

Produce a **Recon Report** (inline or as `recon-report.md`) containing:

1. **App Summary** — one-paragraph description of what it does
2. **Screen Inventory** — table: screen name | purpose | key data shown | key actions
3. **Data Model** — entities identified, relationships, current storage mechanism
4. **State Inventory** — where state lives, what's ephemeral vs persistent
5. **Dependency Map** — libraries grouped by: UI / state / persistence / network / util
6. **Single-User Assumption List** — see Phase 2
7. **Unknowns** — things you couldn't determine; flag for user to clarify

Do not proceed to Phase 2 until the user has confirmed the Recon Report is complete.

---

## Phase 2: Analysis — Single-User Assumption Inventory

Review the recon findings and produce a structured inventory of every single-user
assumption baked into the app. Categorise each:

| Category | Examples |
|---|---|
| **Identity** | No auth, one user context, no session concept |
| **State isolation** | Global/singleton state, module-level vars, no tenancy |
| **Persistence** | Local file, SQLite in app dir, localStorage, electron-store |
| **Paths** | Hardcoded `~/`, `%APPDATA%`, relative paths |
| **Concurrency** | No locking, no optimistic concurrency, no conflict resolution |
| **Permissions** | No RBAC, no resource ownership |
| **Configuration** | Single config file, no per-user settings |
| **Notifications** | In-process only, no push, no cross-client sync |
| **Background work** | Direct calls, no queue, no worker separation |
| **File I/O** | Direct disk access, no abstraction layer |

For each assumption: note **what change is required** and **estimated complexity** (Low/Med/High).

This inventory drives the ADR selection in Phase 4.

---

## Phase 3: Architecture

### 3.1 Architecture Selection

Based on the assumption inventory, select the target architecture pattern.
Read `references/stack-defaults.md` for the default stack decisions.

**Key question: BFF or not?**
Default to **no BFF** (React → FastAPI directly). Recommend BFF only if:
- The UI requires significant server-side aggregation of multiple data sources
- Auth token exchange must be server-side for security (SPA can't hold secrets)
- The app has fundamentally different read and write path shapes

If BFF is warranted, note it as an ADR (see Phase 4). Don't gold-plate.

**Key question: Sync or async backend?**
- Use `async` FastAPI throughout (it's the default in the stack)
- Add RabbitMQ worker if recon reveals: long-running operations, batch jobs,
  file processing, anything that was a blocking call > ~500ms in the original app

### 3.2 C4 Diagrams

Produce C4 diagrams in Mermaid. Minimum: Context + Container level.
Component level only for non-obvious subsystems.

Read `references/c4-patterns.md` for Mermaid C4 templates and conventions.

**Context diagram**: external users, external systems, the new system boundary
**Container diagram**: Frontend (React/Vite), API (FastAPI), DB (Postgres), Cache (Redis),
  Queue (RabbitMQ), Worker(s) — include only containers that are actually needed

Label data flows with the protocol and data type (e.g., "REST/JSON", "AMQP/CloudEvents").

---

## Phase 4: ADRs

Write an ADR for each significant architectural decision. Use the template in
`references/adr-templates.md`.

**Always write ADRs for:**
- Auth mechanism (SSO/OIDC vs username+password vs API key — default: OIDC/SSO)
- Session management (JWT + Redis vs server-side sessions)
- Database (SQLite dev → Postgres prod, SQLAlchemy)
- Multi-tenancy model (row-level, schema-per-tenant, DB-per-tenant)
- State externalisation (what moved from local to Redis)
- Background work (sync vs RabbitMQ worker)

**Write ADRs for if relevant:**
- BFF (if chosen)
- File storage (local → object store: S3/GCS)
- Real-time sync (if app had live-updating UI)
- Deployment topology (k8s, Fly, VPS, etc. — use user's known infrastructure if known)

Each ADR must include: **context** (what the original app did), **decision**, **rationale**,
**alternatives considered**, **consequences**.

---

## Phase 5: PRD

Read `references/prd-template.md` and produce the full PRD.

Key sections the PRD must cover:

1. **Product Overview** — what this is, why it's being built, success criteria
2. **User Roles** — derived from the multi-user model (admin, user, viewer, etc.)
3. **Functional Requirements** — feature-by-feature from screen inventory, rewritten
   for multi-user context (ownership, visibility, sharing, permissions)
4. **Non-Functional Requirements** — auth, security, performance baselines,
   observability (structured logging, metrics), deployment target
5. **Data Model** — entity-relationship overview, tenancy boundaries
6. **API Surface** — endpoint groups (not full OpenAPI, but resource + operations)
7. **Implementation Phases** — ordered milestones for agentic execution:
   - Phase 1: Skeleton (project bootstrap, auth, DB, hello-world endpoint)
   - Phase 2: Core data model + CRUD API
   - Phase 3: Frontend scaffold + auth flow
   - Phase 4: Feature parity with original app
   - Phase 5: Multi-user features (sharing, permissions, notifications)
8. **Out of Scope** — explicit list of what is NOT being built in this pass
9. **Open Questions** — anything the agent will need a human decision on

The PRD must be self-contained — an agent with no prior context must be able to
implement from it without needing to ask clarifying questions (except those listed
in Open Questions).

---

## Output Bundle

Deliver as a set of files:

```
<appname>-multiuser-spec/
├── recon-report.md
├── prd.md
├── adrs/
│   ├── ADR-001-auth.md
│   ├── ADR-002-database.md
│   ├── ADR-003-session-state.md
│   ├── ADR-004-multitenancy.md
│   └── ADR-00N-*.md
└── architecture/
    ├── c4-context.mmd
    └── c4-container.mmd
```

After producing the bundle, ask the user:
1. Does the recon report accurately describe the original app?
2. Are there missing screens, features, or data entities?
3. Are the ADR decisions acceptable, or does anything need revisiting?

Iterate on the bundle until the user signs off, then present the final files.
