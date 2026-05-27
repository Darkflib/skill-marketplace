---
name: agentic-repo-baseline
description: Audit a git repository and ensure it has the minimum baseline files required for agent-driven work — README.md, AGENTS.md, WORKLOG.md, CHANGELOG.md — plus language-specific tooling files for Python (uv) or Node. Use whenever the user wants to "set up a repo for agents", "check the baseline", "add the missing agent files", asks "is this repo agent-ready?", or is about to point Claude Code, Codex, or another agent at a freshly cloned, freshly git-init'd, or inherited repository. Also use as a post-bootstrap verification step after copier or any other scaffolding tool. Trigger even when the user doesn't say "baseline" explicitly — if they're prepping a repo for agent work or asking about AGENTS.md, this is the skill.
---

# Agentic Repo Baseline

Make sure a repo has the minimum files an AI agent needs to operate sensibly:

- **README.md** — human-facing intro
- **AGENTS.md** — agent-facing conventions and commands
- **WORKLOG.md** — in-flight context, bridges sessions
- **CHANGELOG.md** — what's landed (Keep a Changelog format)

Plus language-specific tooling files for Python (uv) or Node.

This is a sanity check, not an enforcer. It inventories what's there, reports what's missing, and creates sensible defaults for the gaps. The templates in `assets/` are starting points — designed to be edited, not treated as final.

## Workflow

### 1. Inventory

Run the inventory script and read the JSON output:

```bash
python scripts/check_baseline.py <repo-path>
```

The report covers:
- Presence of each baseline file
- Detected language(s) — Python, Node, or both
- Language-specific tooling state (pyproject.toml, package.json, .gitignore, ruff/mypy config)
- Git status — whether the directory is a git repo and whether it has any commits

If you can't run the script (no Python execution environment, restricted shell, etc.), do the equivalent checks inline with `ls`, `test -f`, and `git -C <repo> rev-parse HEAD`. The script just makes it deterministic.

### 2. Report and confirm

Summarise the findings in a few lines: what's present, what's missing, detected language(s), git state. Then ask the user what they want created. Don't lecture about why each file matters — they asked for the skill, they know. Just lay out the gaps and let them choose.

If everything is already present, say so and stop. Don't manufacture work.

### 3. Create missing baseline files from templates

For each missing file the user wants created, copy the template from `assets/` to the repo and fill the placeholders:

| Template | Destination | Placeholders |
|---|---|---|
| `assets/README.md.template` | `<repo>/README.md` | `{{ project_name }}`, `{{ project_summary }}` |
| `assets/AGENTS.md.template` | `<repo>/AGENTS.md` | `{{ project_name }}`, `{{ project_summary }}` |
| `assets/WORKLOG.md.template` | `<repo>/WORKLOG.md` | _(none)_ |
| `assets/CHANGELOG.md.template` | `<repo>/CHANGELOG.md` | _(none)_ |

If you can infer `project_name` from the directory name or the git remote, do so and confirm. If you can't infer `project_summary`, ask once — a one-liner is fine, the user will refine it later.

### 4. Language-specific gaps

The script reports tooling presence both at the repo root (e.g. `pyproject_toml_at_root`) and as a list of all locations found in the tree (e.g. `pyproject_toml_locations: ["backend/pyproject.toml"]`). This matters for monorepos.

**Layout rule of thumb:** the four baseline files (README, AGENTS, WORKLOG, CHANGELOG) always live at the repo root — they describe the *repo* as a whole. Tooling manifests (`pyproject.toml`, `package.json`) live wherever the sub-package lives. A backend/frontend monorepo typically has `backend/pyproject.toml` and `frontend/package.json`, no root-level manifest.

**Python (`python` in `languages_detected`):**

- `.py` files present but no `pyproject.toml` anywhere → offer `uv init` (creates pyproject.toml and `.python-version`). Don't run without confirmation.
- `pyproject.toml` exists at root and lacks `[tool.ruff]` or `[tool.mypy]` → offer to add them. Canonical block:

  ```toml
  [tool.ruff]
  target-version = "py312"
  line-length = 100

  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]

  [tool.mypy]
  python_version = "3.12"
  strict = true
  warn_unused_ignores = true
  ```

- No `.gitignore` at root → copy `assets/python.gitignore`. If a root `.gitignore` exists but lacks Python entries, merge rather than overwrite.

**Node (`node` in `languages_detected`):**

- No `package.json` anywhere but JS/TS files present → offer `npm init -y`.
- No `.gitignore` at root → copy `assets/node.gitignore` (merge if one exists).

**Both languages detected (monorepo):**

- Baseline files still go at repo root only.
- For `.gitignore` at root, merge entries from both `python.gitignore` and `node.gitignore`. A single root `.gitignore` covering everything is usually cleaner than per-subdir ones.
- Don't add a root `pyproject.toml` or root `package.json` if the sub-packages already have their own — that creates ambiguity about which is canonical.

**Repo is structurally empty (no source, no manifest):**

- Don't create language-specific files yourself. Ask whether the user wants to bootstrap a real project structure (e.g. via copier-bootstrap if they have a template handy) or just lay down the baseline and populate later. Either is fine.

### 5. Git state

Two cases worth handling explicitly:

- **Not a git repo** (`.git` directory missing): ask whether to run `git init`. Worth noting that Claude Code's agent-team worktree workflow needs an initialised repo with at least one commit, so if the user plans to use that, init is necessary. Don't configure a remote — that's their call.
- **Git repo but no commits** (init'd but empty): after creating baseline files, offer to make the initial commit. A good default message is `chore: agentic baseline files`. Don't push.

If the repo already has commits, just leave git alone.

### 6. Summary

End with a short summary: what was created, what was modified, what was left alone. Point at AGENTS.md and suggest the user reads it through and edits it before kicking off agent work. The template is intentionally generic at the edges — the value is in the project-specific edits the user adds.

## Notes on the templates

**AGENTS.md** is synthesised from Mike's general development conventions, with both Python and Node sections present by default. Most of his projects span both (FastAPI backend + React frontend), so leaving both in is usually right. If the project is single-language, prune the irrelevant section before the agent reads it.

**WORKLOG.md** uses three sections: "In progress", "Up next", "Done". Items move from Up next → In progress → Done as work flows, and Done entries periodically get rolled up into CHANGELOG.md when releases happen.

**CHANGELOG.md** uses Keep a Changelog 1.1.0 with the standard sub-headings (Added/Changed/Deprecated/Removed/Fixed/Security) under an `[Unreleased]` section.

**README.md** is a skeleton — Project Name, Summary, Quick start, Configuration, Documentation pointers, Licence. Pointers go to AGENTS.md, WORKLOG.md, and CHANGELOG.md so the structure is discoverable from the front door.

## What this skill deliberately doesn't do

- No CI workflows (`.github/workflows/`) — separate concern.
- No dependency installation — `uv sync` / `npm install` is the user's call.
- No remote or push configuration — deployment-pipeline concern.
- No enforcement — it's a sanity check. Use a pre-commit hook or CI gate if you want enforcement.
- No full project scaffolding — that's copier-bootstrap territory.

## When to defer

If the repo is empty *and* the user wants a fresh project of a known type (FastAPI service, Lambda, CLI, React app), copier-bootstrap gives a richer starting point. Suggest it as an option. This skill is for the cases copier doesn't cover: cloned third-party repos, inherited codebases, quick experiments, and post-copier baseline verification.
