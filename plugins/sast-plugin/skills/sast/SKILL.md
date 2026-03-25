---
name: sast
description: >
  Run a full SAST (Static Application Security Testing) pipeline across a codebase
  or set of files, orchestrating Semgrep, Bandit, Trufflehog, and Safety/pip-audit.
  Produces a structured findings report and a prioritised remediation plan.

  Use this skill whenever the user wants to: audit code for security issues, run
  static analysis, check for secrets or credentials in source, scan Python
  dependencies for CVEs, review a PR or branch for new vulnerabilities, set up
  a pre-commit or CI security gate, generate a security report, triage SAST
  findings, or get fix recommendations for security issues. Also trigger when the
  user mentions any of: Semgrep, Bandit, Trufflehog, Safety, pip-audit, SAST,
  secrets scanning, dependency audit, or CVE scanning.
---

# SAST Skill

Orchestrates a four-tool SAST pipeline, normalises findings into a unified
severity model, diffs against a baseline for delta/CI mode, and produces:

1. **Structured findings report** — Markdown summary + machine-readable JSON
2. **Prioritised remediation plan** — ranked action list with fix guidance

---

## Quick Reference

| Mode | When to use | Baseline behaviour |
|------|-------------|-------------------|
| `audit` | Full project scan, initial review | Regenerates baseline |
| `pr` | Ad-hoc code review / branch diff | Diffs against existing baseline |
| `ci` | Pre-commit gate, pipeline step | Diffs; non-zero exit on NEW findings ≥ MEDIUM |

Default mode: `audit` if no baseline exists, `pr` otherwise.

---

## Step 0 — Determine Context

Before running anything, establish:

1. **Target path** — file, directory, or Git ref. If not given, use CWD.
2. **Language(s)** — detect from file extensions if not stated. Python and JS/TS
   have distinct rule sets; note both if mixed.
3. **Mode** — `audit`, `pr`, or `ci`. Infer from context (PR mention → `pr`,
   CI/pipeline mention → `ci`, otherwise `audit`).
4. **Fix suggestions requested?** — Default: no. Opt-in when user says "suggest
   fixes", "how do I fix", or similar.
5. **Baseline file** — default path: `.sast-baseline.json` in project root.

---

## Step 1 — Preflight Checks

Check tool availability. For each tool, attempt version probe; note missing tools
but **do not abort** — run what's available and report gaps clearly.

```bash
semgrep --version 2>/dev/null || echo "MISSING: semgrep"
bandit --version 2>/dev/null || echo "MISSING: bandit"
trufflehog --version 2>/dev/null || echo "MISSING: trufflehog"
pip-audit --version 2>/dev/null || safety --version 2>/dev/null || echo "MISSING: safety/pip-audit"
```

**Installation hints** (surface to user if tools missing):

```bash
pip install semgrep bandit pip-audit --break-system-packages
brew install trufflehog           # macOS
# or: docker run ghcr.io/trufflesecurity/trufflehog:latest filesystem .
```

Read `references/tools.md` for full install options, rule set URLs, and
tool-specific flags before proceeding.

---

## Step 2 — Run the Tools

Run all available tools. Capture stdout/stderr; treat non-zero exit as
"findings present", not "tool failed" — distinguish via stderr content.

### Semgrep

```bash
semgrep scan \
  --config auto \
  --json \
  --severity WARNING \
  --no-rewrite-rule-ids \
  <target_path> 2>/dev/null
```

For JS/TS targets, add `--config "p/javascript"`. For Python, `auto` covers it.
See `references/tools.md` → Semgrep section for curated rule sets.

### Bandit (Python only)

```bash
bandit -r <target_path> \
  -f json \
  -ll \
  --quiet \
  2>/dev/null
```

`-ll` = LOW confidence suppressed (MEDIUM+ only). Add `-x tests/,venv/` to
exclude noise from test directories.

### Trufflehog

```bash
trufflehog filesystem <target_path> \
  --json \
  --no-update \
  2>/dev/null
```

For Git repos, prefer `trufflehog git file://<target_path>` to scan history.
Note: Trufflehog exits 0 regardless of findings — parse stdout line count.

### Safety / pip-audit

```bash
# Prefer pip-audit if available
pip-audit --format json --output - 2>/dev/null

# Fallback to Safety
safety check --json 2>/dev/null
```

If neither a `requirements*.txt` nor a `pyproject.toml` is present, note this
and skip rather than producing a spurious "no vulnerabilities" result.

---

## Step 3 — Normalise Findings

Map each tool's output to the unified finding schema (see `references/severity.md`
for full mapping tables):

```json
{
  "id": "<tool>-<hash-of-path+rule>",
  "tool": "semgrep|bandit|trufflehog|pip-audit",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
  "confidence": "HIGH|MEDIUM|LOW",
  "category": "secret|vuln|sca|misconfig",
  "rule_id": "...",
  "title": "...",
  "description": "...",
  "file": "...",
  "line_start": 0,
  "line_end": 0,
  "cwe": ["CWE-XXX"],
  "cvss": null,
  "fix_available": false,
  "suppressed": false
}
```

**Default severity filter:** Drop `INFO` from the report unless user requests
verbose output. Surface `MEDIUM`, `HIGH`, `CRITICAL` prominently. Keep `LOW`
in JSON but de-emphasise in Markdown.

---

## Step 4 — Baseline Delta (pr / ci modes)

If `.sast-baseline.json` exists and mode is `pr` or `ci`:

1. Load baseline findings (array of finding objects, keyed by `id`).
2. Classify each current finding as:
   - `new` — not in baseline
   - `resolved` — in baseline but not in current scan
   - `existing` — present in both
3. In `ci` mode: if any `new` findings with severity ≥ MEDIUM exist, set
   exit flag (report this clearly; do not actually exit Claude's process).
4. Report focuses on `new` findings; `existing` findings summarised only.

In `audit` mode, write/overwrite `.sast-baseline.json` with current findings.

---

## Step 5 — Build the Report

### Markdown Report structure

```
# SAST Report — <project name> — <ISO date>

## Executive Summary
<1–2 sentences: overall posture, critical count, new-vs-existing split>

## Findings by Severity

### 🔴 CRITICAL  (N findings)
### 🟠 HIGH      (N findings)
### 🟡 MEDIUM    (N findings)
### 🟢 LOW       (N findings — detail in JSON)

## Secrets / Credential Exposure
<Trufflehog findings, always surfaced regardless of severity mapping>

## Dependency Vulnerabilities (SCA)
<pip-audit / Safety findings, with CVE IDs and CVSS scores where available>

## Tool Coverage
<table: tool | status | findings count | rule set used>

## Baseline Delta (pr/ci mode only)
<new / resolved / existing counts>
```

Each finding block:
```
### <severity badge> <title>
- **File:** `path/to/file.py:42`
- **Rule:** `<rule_id>`
- **CWE:** CWE-XXX — <name>
- **Description:** <normalised description, 1–2 sentences>
- **Fix hint:** <brief remediation; expand if fix suggestions requested>
```

### JSON output

Write full findings array plus metadata envelope to `sast-report-<timestamp>.json`:

```json
{
  "schema_version": "1.0",
  "generated_at": "<ISO8601>",
  "mode": "audit|pr|ci",
  "target": "<path>",
  "tools_run": [...],
  "summary": { "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0 },
  "findings": [...],
  "baseline_delta": { "new": 0, "resolved": 0, "existing": 0 }
}
```

---

## Step 6 — Prioritised Remediation Plan

After the report, produce a ranked action list:

**Ranking formula** (descending priority):
1. CRITICAL, HIGH confidence secrets (exfiltration risk, immediate)
2. CRITICAL vulns (RCE, injection, auth bypass)
3. HIGH vulns / HIGH confidence MEDIUM
4. SCA findings with CVSS ≥ 7.0 and fix available
5. Remaining MEDIUM
6. LOW / informational

For each item in the plan:

```
## Priority N — <title>
**Risk:** <1 sentence why this matters>
**Effort:** Low | Medium | High
**Action:** <concrete remediation step — rotate cred, patch dep, refactor call>
**References:** <CWE link, CVE link, Semgrep rule docs>
```

If fix suggestions were requested, append a `**Suggested fix:**` block with a
corrected code snippet. Mark clearly as AI-suggested; recommend human review
before merge.

---

## Step 7 — Deliver Outputs

1. Print Markdown report inline in the conversation.
2. Save JSON to `sast-report-<timestamp>.json` and present the file.
3. If baseline was regenerated (`audit` mode), note the new `.sast-baseline.json`
   location.
4. Summarise any tool gaps (missing tools, skipped checks) at the end.

---

## Edge Cases & Guard Rails

- **No findings:** State explicitly "No findings above INFO threshold". Do not
  produce an empty findings list silently.
- **Trufflehog false positives:** If a secret finding looks like a test fixture
  or example key, note it as "likely test/example credential — verify manually".
- **Monorepos:** If target contains multiple `requirements*.txt` or
  `pyproject.toml`, run pip-audit once per manifest and aggregate.
- **Large codebases:** If Semgrep takes > 60s, note it; suggest `--include` or
  `--exclude` flags to scope the scan.
- **Git history scanning:** Trufflehog `git` mode can be slow on deep histories;
  add `--since-commit HEAD~50` for PR mode.
- **Suppressed findings:** Honour `# nosec` (Bandit) and `# nosemgrep` inline
  suppressions but count and report them separately.

---

## Reference Files

- `references/tools.md` — Tool-specific flags, rule sets, install options,
  known quirks. **Read before Step 2 if unfamiliar with a tool's current CLI.**
- `references/severity.md` — Severity mapping tables for each tool, CWE
  taxonomy, CVSS → severity mapping. **Read before Step 3.**
