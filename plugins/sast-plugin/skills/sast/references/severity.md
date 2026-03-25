# Severity Mapping & CWE Taxonomy

## Table of Contents
1. [Unified Severity Model](#unified-severity-model)
2. [Tool Severity Mappings](#tool-severity-mappings)
3. [Category Taxonomy](#category-taxonomy)
4. [CWE Quick Reference](#cwe-quick-reference)
5. [Prioritisation Tiebreakers](#prioritisation-tiebreakers)

---

## Unified Severity Model

All findings are normalised to this five-level model:

| Level | Badge | Definition | Default visibility |
|-------|-------|------------|--------------------|
| CRITICAL | 🔴 | Active credential / RCE / auth bypass | Always shown |
| HIGH | 🟠 | Exploitable without special conditions | Always shown |
| MEDIUM | 🟡 | Exploitable with conditions or chaining | Always shown |
| LOW | 🟢 | Defence-in-depth / best practice | JSON only (summary count in report) |
| INFO | ⚪ | Informational / style | Suppressed by default |

Confidence is tracked separately and affects prioritisation within a severity
band, but does not change the band itself (see tiebreakers below).

---

## Tool Severity Mappings

### Semgrep → Unified

| Semgrep | Metadata impact/likelihood | Unified |
|---------|---------------------------|---------|
| ERROR | HIGH/HIGH | CRITICAL |
| ERROR | any other | HIGH |
| WARNING | HIGH confidence | MEDIUM |
| WARNING | MEDIUM/LOW confidence | LOW |
| INFO | any | INFO |

Special case: rules in `p/secrets` always floor at HIGH regardless of Semgrep level.

### Bandit → Unified

| Bandit severity | Bandit confidence | Unified |
|----------------|-------------------|---------|
| HIGH | HIGH | HIGH |
| HIGH | MEDIUM | HIGH |
| HIGH | LOW | MEDIUM |
| MEDIUM | HIGH | MEDIUM |
| MEDIUM | MEDIUM | LOW |
| MEDIUM | LOW | LOW |
| LOW | any | INFO |

Override rules:
- B105, B106, B107 (hardcoded password) → CRITICAL (regardless of confidence)
- B201 (Flask debug) → HIGH
- B301 (pickle) + B302 (marshal) → HIGH
- B501, B502 (SSL/TLS disable) → CRITICAL

### Trufflehog → Unified

| Verified | Detector type | Unified |
|----------|--------------|---------|
| true | Any | CRITICAL |
| false | Named detector (AWS, GCP, GitHub, etc.) | HIGH |
| false | Generic/entropy | MEDIUM |

Named detectors include: AWS, Azure, GCP, GitHub, GitLab, Slack, Stripe,
Twilio, SendGrid, Heroku, npm, PyPI, and 700+ others.

### pip-audit → Unified

Map via CVSS score (see tools.md). Where CVSS is absent, use MEDIUM.
Escalation rule: if a fix version is available, escalate LOW→MEDIUM and
MEDIUM→HIGH to reflect that leaving it unpatched is an active choice.

---

## Category Taxonomy

| Category | Description | Primary tools |
|----------|-------------|---------------|
| `secret` | Credentials, API keys, tokens in code/history | Trufflehog, Semgrep p/secrets |
| `vuln` | Code-level security vulnerabilities | Semgrep, Bandit |
| `sca` | Third-party dependency CVEs | pip-audit, Safety |
| `misconfig` | Security misconfigurations | Bandit, Semgrep |

Sub-categories for `vuln`:

| Sub-category | CWE family | Examples |
|-------------|------------|---------|
| `injection` | CWE-74 to CWE-94 | SQL, command, LDAP, XPath injection |
| `crypto` | CWE-310 to CWE-340 | Weak hash, hardcoded key, insecure random |
| `auth` | CWE-287 to CWE-308 | Auth bypass, session fixation |
| `deserialization` | CWE-502 | pickle, marshal, yaml.load |
| `path-traversal` | CWE-22 | open() with user input |
| `ssrf` | CWE-918 | requests with user-controlled URL |
| `xxe` | CWE-611 | XML parsing without entity limits |
| `tls` | CWE-295, CWE-326 | TLS verify=False, weak ciphers |
| `info-disclosure` | CWE-200 | Stack traces, debug endpoints |

---

## CWE Quick Reference

Commonly encountered in Python codebases:

| CWE | Name | Common trigger |
|-----|------|----------------|
| CWE-20 | Improper Input Validation | Missing validation on external input |
| CWE-22 | Path Traversal | `open(user_input)` |
| CWE-78 | OS Command Injection | `subprocess.call(shell=True)` |
| CWE-79 | XSS | Unescaped output in templates |
| CWE-89 | SQL Injection | String-formatted SQL queries |
| CWE-94 | Code Injection | `eval()`, `exec()` |
| CWE-200 | Info Disclosure | Debug mode, verbose errors |
| CWE-259 | Hardcoded Password | `password = "..."` literal |
| CWE-295 | Improper Certificate Validation | `verify=False` |
| CWE-326 | Inadequate Encryption Strength | MD5, SHA1 for security |
| CWE-327 | Broken/Risky Crypto | DES, RC4, ECB mode |
| CWE-328 | Reversible One-Way Hash | MD5 for passwords |
| CWE-330 | Insufficient Randomness | `random` instead of `secrets` |
| CWE-502 | Deserialisation of Untrusted Data | `pickle.loads()` |
| CWE-601 | Open Redirect | Unvalidated redirect URL |
| CWE-611 | XXE | `lxml` / `xml.etree` with untrusted input |
| CWE-918 | SSRF | `requests.get(user_url)` |
| CWE-943 | NoSQL Injection | MongoDB query with user input |

---

## Prioritisation Tiebreakers

When two findings share a unified severity level, apply these tiebreakers in order:

1. **Category:** `secret` > `vuln` (injection/auth) > `sca` (fix available) >
   `vuln` (crypto/misconfig) > `sca` (no fix) > `misconfig`
2. **Confidence:** HIGH > MEDIUM > LOW
3. **Exploitability:** Network-accessible code paths > internal/admin paths > test/utility code
4. **Fix cost:** "Change one line" > "Refactor module" > "Upgrade dependency" >
   "Architectural change"
5. **Verification:** Trufflehog `verified: true` always floats to top within CRITICAL

### Effort Estimation Heuristics

| Action type | Effort label |
|-------------|-------------|
| Rotate a credential | Low |
| Upgrade a pinned dependency version | Low |
| Replace `random` with `secrets` | Low |
| Add input validation to a function | Medium |
| Replace `pickle` with `json`/`msgpack` | Medium |
| Refactor SQL to parameterised queries | Medium |
| Restructure auth flow | High |
| Migrate TLS configuration | High |
| Architectural SSO/credential management change | High |
