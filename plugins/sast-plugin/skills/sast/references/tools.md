# SAST Tools Reference

## Table of Contents
1. [Semgrep](#semgrep)
2. [Bandit](#bandit)
3. [Trufflehog](#trufflehog)
4. [pip-audit / Safety](#pip-audit--safety)
5. [Installation Summary](#installation-summary)

---

## Semgrep

### Recommended Rule Sets

| Rule set | Use case | Config string |
|----------|----------|---------------|
| `auto` | Python general (auto-selects) | `--config auto` |
| `p/python` | Explicit Python ruleset | `--config p/python` |
| `p/javascript` | JS/TS | `--config p/javascript` |
| `p/secrets` | Secrets (complements Trufflehog) | `--config p/secrets` |
| `p/owasp-top-ten` | OWASP coverage | `--config p/owasp-top-ten` |
| `p/django` | Django-specific | `--config p/django` |
| `p/flask` | Flask-specific | `--config p/flask` |
| `p/fastapi` | FastAPI (community) | `--config p/fastapi` |

For comprehensive Python coverage: `--config auto --config p/secrets --config p/owasp-top-ten`

Multiple `--config` flags are additive. Dedup by rule ID is automatic.

### Severity Flags

```bash
--severity INFO      # Everything (noisy)
--severity WARNING   # Medium+ (recommended default)
--severity ERROR     # High/Critical only (CI gate)
```

Note: Semgrep's severity levels (`INFO`/`WARNING`/`ERROR`) map to the unified
model as: INFO→INFO, WARNING→MEDIUM, ERROR→HIGH. Rules tagged `CRITICAL` in
metadata are passed through as CRITICAL.

### Useful Additional Flags

```bash
--exclude "tests,venv,.venv,node_modules,migrations"
--include "*.py,*.js,*.ts"
--max-target-bytes 5000000    # Skip files > 5MB
--timeout 30                  # Per-file timeout (seconds)
--metrics off                 # Disable telemetry
--no-git-ignore               # Scan gitignored files too (useful for secrets)
```

### JSON Output Fields of Interest

```json
{
  "results": [
    {
      "check_id": "python.lang.security.audit.hardcoded-password-default-arg",
      "path": "app/config.py",
      "start": { "line": 42 },
      "end": { "line": 42 },
      "extra": {
        "message": "...",
        "severity": "WARNING",
        "metadata": {
          "cwe": ["CWE-259"],
          "confidence": "HIGH",
          "impact": "MEDIUM",
          "likelihood": "LOW"
        }
      }
    }
  ],
  "errors": [],
  "stats": { "total_time": 1.2 }
}
```

### Known Quirks

- `auto` config phones home to semgrep.dev for rule updates; `--metrics off`
  disables analytics but not rule fetching. Use `--config /path/to/rules` for
  air-gapped environments.
- Exit code 1 means findings present (not tool error). Exit code 2 means error.
  Parse `errors[]` field to distinguish.
- Rule IDs can change between versions; use `--no-rewrite-rule-ids` to preserve
  original IDs for stable baseline comparison.

---

## Bandit

### Recommended Invocation

```bash
bandit -r <path> \
  -f json \
  -ll \               # LOW confidence suppressed
  -ii \               # LOW severity suppressed (use -i for MEDIUM+)
  --quiet \
  -x <path>/tests,<path>/venv,<path>/.venv \
  2>/dev/null
```

Drop `-ii` to include LOW severity (useful for full audit mode).

### Severity / Confidence Matrix

Bandit reports `severity` (LOW/MEDIUM/HIGH) and `confidence` (LOW/MEDIUM/HIGH)
independently. Map to unified model:

| Bandit severity | Bandit confidence | Unified severity |
|----------------|-------------------|-----------------|
| HIGH           | HIGH/MEDIUM       | HIGH            |
| HIGH           | LOW               | MEDIUM          |
| MEDIUM         | HIGH              | MEDIUM          |
| MEDIUM         | MEDIUM/LOW        | LOW             |
| LOW            | any               | INFO            |

Exception: B105, B106, B107 (hardcoded passwords) → always CRITICAL regardless
of confidence, given potential secret exposure.

### Notable Test IDs

| Test ID | Description | Priority |
|---------|-------------|----------|
| B101    | assert statements | LOW |
| B102    | exec() | HIGH |
| B103    | file permissions | MEDIUM |
| B104    | bind all interfaces | HIGH |
| B105-107 | hardcoded passwords | CRITICAL |
| B110    | try/except/pass | LOW |
| B201    | Flask debug=True | HIGH |
| B301    | pickle | HIGH |
| B303    | MD5/SHA1 | MEDIUM |
| B311    | random (not cryptographic) | MEDIUM |
| B324    | hashlib weak | HIGH |
| B501-506 | TLS/SSL issues | HIGH |
| B601-608 | injection | HIGH |
| B701-703 | Jinja2/Mako injection | HIGH |

### JSON Output Fields of Interest

```json
{
  "results": [
    {
      "test_id": "B201",
      "test_name": "flask_debug_true",
      "issue_text": "A Flask app appears to be run with debug=True",
      "filename": "app/main.py",
      "line_number": 42,
      "issue_severity": "HIGH",
      "issue_confidence": "MEDIUM",
      "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b201_flask_debug_true.html"
    }
  ],
  "metrics": {
    "_totals": { "SEVERITY.HIGH": 1, "SEVERITY.MEDIUM": 2 }
  }
}
```

### Known Quirks

- Bandit exits 1 on findings, 0 on clean, 2 on error. Same pattern as Semgrep.
- Does not understand type annotations well; false positives on annotated
  `Optional[str]` default args. Use `# nosec B107` to suppress.
- `--skip` flag takes test IDs, not names: `--skip B101,B110`.

---

## Trufflehog

### Recommended Invocation

**Filesystem (files only):**
```bash
trufflehog filesystem <path> \
  --json \
  --no-update \
  --concurrency 4 \
  2>/dev/null
```

**Git history (preferred for repos):**
```bash
trufflehog git file://<path> \
  --json \
  --no-update \
  --since-commit HEAD~50 \    # PR mode: limit depth
  --branch <branch> \         # optional
  2>/dev/null
```

For full audit mode, omit `--since-commit` to scan entire history.

### Docker Alternative (no install required)

```bash
docker run --rm \
  -v "$PWD:/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  filesystem /repo --json --no-update
```

### Severity Mapping

Trufflehog does not emit severity levels directly. Map as follows:

| Detector type | Verified | Unified severity |
|--------------|----------|-----------------|
| Any secret | `verified: true` | CRITICAL |
| Any secret | `verified: false` | HIGH |
| Entropy-only | n/a | MEDIUM |

`verified: true` means Trufflehog successfully validated the credential against
its API. These are live, active credentials — treat as CRITICAL/P0.

### JSON Output Structure (one JSON object per line, not array)

```json
{
  "SourceMetadata": {
    "Data": {
      "Filesystem": { "file": "config/settings.py", "line": 42 }
    }
  },
  "SourceID": 1,
  "DetectorName": "AWS",
  "DecoderName": "PLAIN",
  "Verified": true,
  "Raw": "AKIA...",
  "RawV2": "",
  "Redacted": "AKIA****",
  "ExtraData": { "account": "123456789" },
  "StructuredData": null
}
```

Parse with `jq -s '.'` to convert NDJSON to array, or process line by line.
**Never log `Raw` field** — it contains the actual secret.

### Known Quirks

- Always exits 0, even with findings. Check stdout line count or `jq length`.
- `--no-update` prevents auto-update noise on stdout; always include it.
- Git mode can be extremely slow on repos with large binary history. Use
  `--include-paths` or `--since-commit` to scope.
- Some detectors (e.g., generic API key patterns) produce high false-positive
  rates — flag these as "verify manually" rather than treating as confirmed.

---

## pip-audit / Safety

### pip-audit (preferred)

```bash
# Scan current environment
pip-audit --format json --output -

# Scan from requirements file
pip-audit -r requirements.txt --format json --output -

# Scan from pyproject.toml (PEP 517)
pip-audit --format json --output -   # auto-detects

# Include dev dependencies
pip-audit --format json --output - --require-hashes false
```

pip-audit queries the OSV (Open Source Vulnerabilities) database by default,
which aggregates NVD, GitHub Advisory, and PyPI advisories.

### Safety (fallback)

```bash
safety check --json
safety check -r requirements.txt --json
```

Safety 3.x requires a free API key for full results (`safety auth login`).
Safety 2.x works without a key but against a smaller DB. Prefer pip-audit.

### JSON Output — pip-audit

```json
{
  "dependencies": [
    {
      "name": "requests",
      "version": "2.25.0",
      "vulns": [
        {
          "id": "GHSA-j8r2-6x86-q33q",
          "fix_versions": ["2.31.0"],
          "aliases": ["CVE-2023-32681"],
          "description": "..."
        }
      ]
    }
  ]
}
```

### Severity Mapping for SCA Findings

pip-audit/Safety don't always include CVSS scores. Use this mapping:

| Signal | Unified severity |
|--------|-----------------|
| CVE with CVSS ≥ 9.0 | CRITICAL |
| CVE with CVSS 7.0–8.9 | HIGH |
| CVE with CVSS 4.0–6.9 | MEDIUM |
| CVE with CVSS < 4.0 | LOW |
| Advisory without CVSS | MEDIUM (default) |
| Fix available | Escalate one level if MEDIUM → HIGH |

CVSS scores can be looked up via `https://api.osv.dev/v1/vulns/<ID>` if not
included in the output.

### Known Quirks

- pip-audit scans the **installed** environment by default, not just a
  requirements file. In CI, run in a clean venv to avoid scanning system
  packages.
- Safety 3.x exits 64 for vulnerabilities found (not 1). Check exit code
  handling carefully.
- Some PyPI packages carry multiple CVE aliases for the same vuln; dedup by
  OSV ID (`GHSA-*`) rather than CVE ID.

---

## Installation Summary

```bash
# All Python tools at once
pip install semgrep bandit pip-audit --break-system-packages

# Or in a dedicated security venv
python -m venv ~/.sast-venv
source ~/.sast-venv/bin/activate
pip install semgrep bandit pip-audit

# Trufflehog — pick one:
brew install trufflehog                                          # macOS
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin   # Linux
docker run ghcr.io/trufflesecurity/trufflehog:latest ...        # Docker
```

**Pinned versions for reproducible CI (update periodically):**
```
semgrep>=1.70.0
bandit>=1.7.8
pip-audit>=2.7.0
```
