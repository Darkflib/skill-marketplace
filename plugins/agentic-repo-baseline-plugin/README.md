# Agentic Repo Baseline - Usage Guide

Audits a git repository for the minimum files an AI agent needs to operate sensibly, reports the gaps, and creates sensible defaults for whatever is missing. It's a sanity check, not an enforcer.

## What it checks for

| File | Purpose |
|------|---------|
| `README.md` | Human-facing intro |
| `AGENTS.md` | Agent-facing conventions and commands |
| `WORKLOG.md` | In-flight context that bridges sessions ("In progress" / "Up next" / "Done") |
| `CHANGELOG.md` | What's landed, in [Keep a Changelog](https://keepachangelog.com) 1.1.0 format |

Plus language-specific tooling: `pyproject.toml` (+ `ruff`/`mypy` config) and `.gitignore` for Python (uv), `package.json` and `.gitignore` for Node — with monorepo-aware placement.

## Use Cases

- **Freshly cloned / inherited repo**: get it agent-ready before pointing Claude Code or Codex at it
- **Post-`git init`**: lay down baseline files and make the first commit
- **Post-bootstrap verification**: confirm a copier-scaffolded repo has everything agents expect
- **"Is this repo agent-ready?"**: quick inventory of what's present and what's missing

## Quick Usage

Once installed, ask Claude things like:

- "Set this repo up for agents"
- "Check the baseline / is this repo agent-ready?"
- "Add the missing agent files"

## Workflow

1. **Inventory** — runs `scripts/check_baseline.py <repo-path>` and reads the JSON report (presence of each file, detected languages, tooling state, git status)
2. **Report and confirm** — summarises gaps and asks what to create; if nothing's missing, says so and stops
3. **Create from templates** — copies templates from `assets/`, filling `{{ project_name }}` / `{{ project_summary }}` placeholders (inferred from directory/remote where possible)
4. **Language gaps** — offers `uv init` / `npm init`, ruff/mypy blocks, and the right `.gitignore` (merging rather than overwriting)
5. **Git state** — offers `git init` and/or an initial commit (`chore: agentic baseline files`); never configures a remote or pushes
6. **Summary** — what was created, modified, and left alone

## CLI Usage

```bash
# Inventory a repo and print a JSON report
python scripts/check_baseline.py /path/to/repo
```

If a Python execution environment isn't available, the same checks can be done inline with `ls`, `test -f`, and `git -C <repo> rev-parse HEAD`.

## What it deliberately doesn't do

- No CI workflows, no dependency installation, no remote/push configuration
- No enforcement (use a pre-commit hook or CI gate for that)
- No full project scaffolding — that's [copier-bootstrap](../copier-bootstrap-plugin) territory

## When to defer

If the repo is empty *and* the user wants a fresh project of a known type (FastAPI, Lambda, CLI, React), `copier-bootstrap-plugin` gives a richer starting point. This skill is for the cases copier doesn't cover: cloned third-party repos, inherited codebases, quick experiments, and post-copier baseline verification.
