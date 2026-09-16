# Skill Marketplace

A collection of plugins and skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Security Notice

As with all plugins and skills, **exercise caution when installing from untrusted sources**. Plugins can execute code on your machine and access your filesystem. Review the contents of any plugin before installing it.

## Support

These plugins are provided on a **best-effort basis**. There are no guarantees of ongoing maintenance or support.

Issues and pull requests are welcome.

## Installation

Add the marketplace, then install plugins by name. Each plugin ships a single skill.

```
/plugin marketplace add Darkflib/skill-marketplace
/plugin install kroki-plugin@skill-marketplace
```

## Available Skills

| Skill | Plugin | Description |
|-------|--------|-------------|
| **agentic-repo-baseline** | `agentic-repo-baseline-plugin` | Audit a git repo for the baseline files agents need (README.md, AGENTS.md, WORKLOG.md, and CHANGELOG.md, plus uv or Node tooling) and create sensible defaults for the gaps. Also useful as a post-bootstrap check. |
| **app-to-multiuser** | `app-to-multiuser-plugin` | Reverse-engineer a single-user GUI or Electron app into an implementation-ready PRD and ADR bundle, with C4 diagrams, for porting it to a multi-user web application. |
| **copier-bootstrap** | `copier-bootstrap-plugin` | Bootstrap new projects using Copier templates. Supports FastAPI services, RabbitMQ workers, CLI tools, React frontends, AWS Lambda functions, and Google Cloud Functions. |
| **current-github-action-versions** | `current-github-action-versions-plugin` | Version floors for common GitHub Actions (core, Docker, release, supply chain, and deploy) so new and edited workflows avoid deprecation warnings. Includes SHA-pinning guidance. |
| **found-footage-scare** | `found-footage-scare-plugin` | Build found-footage / CCTV-style jumpscare videos from stills with ffmpeg. Covers pacing the lull, reveal and hit, audio sting design and gain staging, and making output pass as a genuine camera export. |
| **kroki** | `kroki-plugin` | Generate diagrams from plain text using a Kroki server. Supports PlantUML, Mermaid, GraphViz/DOT, D2, Structurizr, Ditaa, Svgbob, Excalidraw, and more. |
| **project-planning** | `project-planning-plugin` | Structured 4-step methodology for planning and breaking down new software projects. Follows a human-in-the-loop gated process with clear deliverables at each stage. |
| **python-cli-scaffold** | `python-cli-scaffold-plugin` | Scaffold Python CLI tools with Click and Rich. Includes command groups, progress bars, tables, spinners, structured logging, testing, and Docker support. |
| **python-fastapi-scaffold** | `python-fastapi-scaffold-plugin` | Scaffold modern Python FastAPI projects with UV, Docker, K8s/Cloud Run deployment templates, testing, configuration management, and CI/CD patterns. |
| **python-production-versions** | `python-production-versions-plugin` | Authoritative reference for current Python production library versions, deprecated packages, and compatibility issues. Provides version floors with project-local overrides. |
| **python-worker-scaffold** | `python-worker-scaffold-plugin` | Scaffold Python background workers for RabbitMQ with signed CloudEvents, structured logging, Docker, K8s manifests, retry logic, and dead letter queues. |
| **sast** | `sast-plugin` | Run a full SAST pipeline across a codebase using Semgrep, Bandit, Trufflehog, and Safety/pip-audit. Produces structured findings and a prioritised remediation plan. |
| **term-extractor** | `term-extractor-plugin` | Extract technical terms, acronyms, and domain vocabulary from text into structured YAML format for glossary and index generation. |
