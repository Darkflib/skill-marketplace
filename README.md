# Skill Marketplace

A collection of plugins and skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Security Notice

As with all plugins and skills, **exercise caution when installing from untrusted sources**. Plugins can execute code on your machine and access your filesystem. Review the contents of any plugin before installing it.

## Support

These plugins are provided on a **best-effort basis**. There are no guarantees of ongoing maintenance or support.

Issues and pull requests are welcome.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| **copier-bootstrap** | Bootstrap new projects using Copier templates. Supports FastAPI services, RabbitMQ workers, CLI tools, React frontends, AWS Lambda functions, and Google Cloud Functions. |
| **kroki** | Generate diagrams from plain text using a Kroki server. Supports PlantUML, Mermaid, GraphViz/DOT, D2, Structurizr, Ditaa, Svgbob, Excalidraw, and more. |
| **project-planning** | Structured 4-step methodology for planning and breaking down new software projects. Follows a human-in-the-loop gated process with clear deliverables at each stage. |
| **python-cli-scaffold** | Scaffold Python CLI tools with Click and Rich. Includes command groups, progress bars, tables, spinners, structured logging, testing, and Docker support. |
| **python-fastapi-scaffold** | Scaffold modern Python FastAPI projects with UV, Docker, K8s/Cloud Run deployment templates, testing, configuration management, and CI/CD patterns. |
| **python-production-versions** | Authoritative reference for current Python production library versions, deprecated packages, and compatibility issues. Provides version floors with project-local overrides. |
| **python-worker-scaffold** | Scaffold Python background workers for RabbitMQ with signed CloudEvents, structured logging, Docker, K8s manifests, retry logic, and dead letter queues. |
| **sast** | Run a full SAST pipeline across a codebase using Semgrep, Bandit, Trufflehog, and Safety/pip-audit. Produces structured findings and a prioritised remediation plan. |
| **term-extractor** | Extract technical terms, acronyms, and domain vocabulary from text into structured YAML format for glossary and index generation. |
