# Deprecated & Forked Libraries

**Last Updated**: 2025-11-15

This document tracks libraries that should NOT be used, along with their recommended replacements. This prevents using unmaintained, insecure, or deprecated packages.

---

## ❌ DO NOT USE - Python Libraries

### Unmaintained Security-Critical Libraries

| Deprecated | Replacement | Reason | Last Maintained |
|------------|-------------|--------|-----------------|
| `python-jose` | `jwcrypto>=1.5.0` | Unmaintained, security concerns | ~2023 |
| `pycrypto` | `cryptography>=42.0.0` | Security vulnerabilities, unmaintained | 2018 |
| `pycryptodome` | `cryptography>=42.0.0` | Fork of pycrypto, prefer cryptography | Ongoing |
| `passlib` | `argon2-cffi>=23.0.0` or bcrypt | Unmaintained | ~2020 |

**Migration Example (python-jose → jwcrypto)**:
```python
# ❌ OLD (python-jose)
from jose import jwt
token = jwt.encode(payload, key, algorithm='RS256')

# ✅ NEW (jwcrypto)
from jwcrypto import jwt, jwk
token = jwt.JWT(header={"alg": "RS256"}, claims=payload)
token.make_signed_token(key)
```

---

### Task Queue / Message Processing

| Deprecated/Not Recommended | Replacement | Reason |
|---------------------------|-------------|--------|
| `celery` (for new projects) | `aio-pika>=9.4.0` + custom workers | Too heavy, complex config |
| `dramatiq` (with Redis) | `aio-pika>=9.4.0` or Redis Streams direct | Abstraction hides control we need for CloudEvents |
| `rq` | `aio-pika>=9.4.0` | Limited features, Redis-only |

**Why we use aio-pika directly**:
- Need direct RabbitMQ control for CloudEvents signing
- Custom message routing and error handling
- Simpler stack (no Redis requirement)
- Better observability

---

### HTTP Libraries

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `requests-futures` | `httpx>=0.27.0` with async | httpx has better async support |
| `urllib3` (direct use) | `httpx>=0.27.0` | Use higher-level client |

**Note**: `requests` is still fine for sync-only scripts, but prefer `httpx` for new code.

---

### Configuration Management

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `python-decouple` | `pydantic-settings>=2.6.0` | Better type safety, validation |
| `environs` | `pydantic-settings>=2.6.0` | Pydantic provides same features |

**Note**: `python-dotenv` is still fine for loading `.env` files in development, but use Pydantic Settings for actual config management.

---

### Data Validation

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `marshmallow` | `pydantic>=2.9.0` | Pydantic has better performance and typing |
| `cerberus` | `pydantic>=2.9.0` | Pydantic is more Pythonic |
| `voluptuous` | `pydantic>=2.9.0` | Pydantic is more widely used |

---

### ORM/Database

| Deprecated | Notes |
|------------|-------|
| `django.db` (outside Django) | Don't extract Django ORM for standalone use - use SQLAlchemy |
| `peewee` | Fine for small projects, but prefer SQLAlchemy for consistency |

---

## ❌ DO NOT USE - Container Images

### Docker Base Images

| Deprecated | Replacement | Reason | Discontinued Date |
|------------|-------------|--------|-------------------|
| Bitnami images (free tier) | Docker Official Images or Cloud provider images | Free tier discontinued | Sept 2025 |
| Bitnami Helm charts (free) | Official charts or cloud provider charts | Free tier discontinued | Sept 2025 |

**Bitnami Migration Guide**:

```yaml
# ❌ OLD (Bitnami)
FROM bitnami/python:3.12

# ✅ NEW (Docker Official)
FROM python:3.12-slim

# ✅ OR (Chainguard - for security-focused)
FROM cgr.dev/chainguard/python:latest
```

**For Helm Charts**:
- PostgreSQL: Use Cloud provider managed DB or official postgres Docker image
- Redis: Use Cloud provider managed Redis or official redis Docker image  
- RabbitMQ: Use official rabbitmq Docker image with management plugin
- Kafka: Use Confluent official images or Strimzi operator

---

## Python Version Lifecycle

| Version | Status | EOL Date | Use in Production? |
|---------|--------|----------|-------------------|
| 3.8 | EOL | Oct 2024 | ❌ No |
| 3.9 | Security fixes only | Oct 2025 | ⚠️ Migrate away |
| 3.10 | Security fixes only | Oct 2026 | ⚠️ Plan migration |
| 3.11 | Supported | Oct 2027 | ✅ Yes |
| 3.12 | Supported | Oct 2028 | ✅ Yes (recommended) |
| 3.13 | Supported | Oct 2029 | ✅ Yes |

**Recommendation**: Use Python 3.12+ for all new projects.

---

## JavaScript/Node (If Applicable)

### Package Managers

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `npm` (for new projects) | `pnpm` or `bun` | Faster, better disk usage |
| `yarn` v1 | `pnpm` or `yarn` v4 | v1 is in maintenance mode |

### Libraries

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `moment.js` | `date-fns` or `dayjs` | Moment is in maintenance mode |
| `request` | `axios` or `node-fetch` | Deprecated |
| `express-validator` (old) | `zod` | Better TypeScript support |

---

## Breaking Changes to Watch

### SQLAlchemy 1.4 → 2.0
- **Change**: New declarative syntax, async-first
- **Action**: Use 2.0 for new projects, migrate old projects gradually
- **Compatibility**: `alembic>=1.13.0` required for SQLAlchemy 2.0

### Pydantic v1 → v2
- **Change**: Complete rewrite, not backward compatible
- **Action**: Always use v2 for new projects
- **Migration**: Use `pydantic-compat` for gradual migration

### FastAPI 0.100+ 
- **Change**: New exception handler interface
- **Action**: Update exception handlers when upgrading
- **Docs**: https://fastapi.tiangolo.com/release-notes/#breaking-changes

---

## Flagged for Future Review

These libraries are currently fine but should be monitored:

- **Celery**: Heavy and complex, consider alternatives for new projects
- **Django**: Great framework, but we're standardizing on FastAPI for APIs
- **boto3** (AWS SDK): Fine, but consider `aioboto3` for async workloads

---

## Automation Notes

**How to maintain this file**:

1. **Check for unmaintained packages**:
   ```bash
   # Check last release date on PyPI
   pip show <package-name>
   ```

2. **Monitor security advisories**:
   - GitHub Security Advisories
   - Snyk database
   - PyPI security notices

3. **Track deprecation announcements**:
   - Library GitHub repositories
   - Release notes
   - Python packaging announcements

4. **Review quarterly**:
   - Remove entries that are truly obsolete (>5 years)
   - Add new deprecations
   - Update replacement recommendations

**Suggested automation**:
```bash
# Check if deprecated packages are in use
rg "python-jose|pycrypto|passlib" pyproject.toml requirements.txt

# Alert if found in dependencies
```
