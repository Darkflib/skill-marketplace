# App → Multi-User - Usage Guide

Reverse-engineers a single-user GUI or Electron app and produces a fully-specified **PRD + ADR bundle** that an AI coding agent (Claude Code, Codex, etc.) can implement directly. The documents come first; code generation is a secondary output.

## Use Cases

- **Desktop → web**: port an Electron or local GUI app to a networked web app
- **Single-user → SaaS**: add auth, tenancy, and multi-user features to a single-user tool
- **Spec extraction**: turn an existing app codebase into an implementation-ready spec
- **Re-architecture**: produce ADRs and C4 diagrams for a planned rebuild

## Quick Usage

Once installed, ask Claude things like:

- "Convert this app to multi-user"
- "Make this desktop app web-based"
- "Turn this into a SaaS"
- "Network-enable this app"

## Workflow

The skill runs five gated phases — each gates the next, so recon isn't skipped:

1. **Recon** — gather all available evidence (screenshots, source, filesystem layout, dependencies, runtime behaviour) and produce a Recon Report. The most critical phase; everything downstream depends on it.
2. **Analysis** — inventory every single-user assumption (identity, state isolation, persistence, paths, concurrency, permissions, …) with required change and complexity.
3. **Architecture** — select target patterns (BFF or not, sync vs async backend) and produce C4 Context + Container diagrams in Mermaid.
4. **Decisions** — write ADRs for the significant calls (auth, session, database, multi-tenancy, state externalisation, background work).
5. **PRD** — produce a self-contained, implementation-ready product spec with ordered milestones an agent can execute from.

## Output Bundle

```
<appname>-multiuser-spec/
├── recon-report.md
├── prd.md
├── adrs/
│   ├── ADR-001-auth.md
│   ├── ADR-002-database.md
│   └── ADR-00N-*.md
└── architecture/
    ├── c4-context.mmd
    └── c4-container.mmd
```

The PRD is designed to be self-contained — an agent with no prior context should be able to implement from it without clarifying questions (except those listed under Open Questions).

## References

The skill bundles opinionated reference docs it consults during the relevant phase:

- `references/stack-defaults.md` — default target stack (read first)
- `references/c4-patterns.md` — Mermaid C4 templates and conventions
- `references/adr-templates.md` — ADR format
- `references/prd-template.md` — PRD structure

## Related

Pairs well with `agentic-repo-baseline-plugin` (prep the target repo for agent work) and `copier-bootstrap-plugin` (scaffold the new project once the spec is approved).
