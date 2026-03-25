---
name: python-production-versions
description: >
  Authoritative reference for current Python production library versions,
  deprecated packages, and compatibility issues. Use when creating Python
  projects, adding dependencies to pyproject.toml or requirements.txt,
  updating library versions, scaffolding projects, or discussing Python
  library versions. Provides version floors to prevent outdated, unmaintained,
  or incompatible packages. Supports project-local overrides via
  .claude/python-versions.md.
---

# Python Production Versions

## Overview

This skill provides the authoritative reference for Python library versions used in production. It prevents the use of outdated, deprecated, or incompatible packages by maintaining current version information, deprecation notices, and compatibility notes.

The versions in this skill are **lower bounds** — they represent the minimum acceptable versions. Projects may use newer versions. Teams can override or supplement these defaults with a project-local file.

## Local Project Overrides

Before using the bundled references, **always check for a project-local override file**:

1. Look for `.claude/python-versions.md` in the project root
2. If it exists, read it first — **local overrides take precedence** over bundled references
3. Then read the bundled references for any packages not covered locally
4. If there is a conflict, the local file wins

This allows teams to:
- Pin specific versions that differ from the defaults
- Add packages not covered by the bundled references
- Mark additional packages as deprecated for their context
- Document team-specific compatibility issues

### Local override format

The local file (`.claude/python-versions.md`) should follow the same format as the bundled reference files:

```markdown
# Project Python Version Overrides

## Version Pins
| Package | Version | Notes |
|---------|---------|-------|
| fastapi | >=0.116.0 | Pinned higher — we need the new middleware API |
| sqlalchemy | >=2.0.36 | Security fix in 2.0.36 |

## Additional Deprecated Packages
| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| requests | httpx>=0.27.0 | Team standard: async-first |

## Additional Compatibility Notes
- `our-internal-lib>=2.0` requires `pydantic>=2.10.0`
```

## When to Use This Skill

**Always use this skill when**:
- Creating new Python projects or scaffolds
- Adding dependencies to `pyproject.toml` or `requirements.txt`
- Updating Python library versions
- Discussing "what version should I use" for Python packages
- Generating Python project templates
- Reviewing Python dependency specifications

**This skill prevents**:
- Using outdated library versions from training data
- Selecting deprecated or unmaintained Python packages
- Introducing known version conflicts
- Using discontinued container images for Python services

## Reference Files

### references/python.md
**Use for**: Python library versions, version constraints, common stacks

Contains current recommended versions for FastAPI, Pydantic, SQLAlchemy, aio-pika, Click, Rich, and other common Python libraries. Includes version constraint strategies and breaking change notes.

**Read when**: Creating any Python project, adding Python dependencies, or updating libraries.

### references/deprecated.md
**Use for**: Checking if a Python library should be avoided

Contains deprecated, unmaintained, or forked libraries with recommended replacements and migration examples.

**Read when**: A library seems outdated, wondering if there's a better alternative, or encountering unmaintained packages.

### references/compatibility.md
**Use for**: Debugging version conflicts and known issues

Contains known version conflicts, platform-specific issues (macOS ARM, Linux), common error messages and fixes, and database driver version matrices.

**Read when**: Encountering dependency resolution errors, platform-specific build failures, or integration issues between libraries.

### references/containers.md
**Use for**: Docker base images for Python services

Contains recommended Docker base images for Python applications and common companion services (PostgreSQL, Redis, RabbitMQ). Includes multi-architecture build guidance and security best practices.

**Read when**: Creating Dockerfiles for Python services, selecting base images, or setting up docker-compose files.

## Usage Patterns

### Creating a New Project

```
1. Check for .claude/python-versions.md (local overrides)
2. Read references/python.md (bundled versions)
3. Merge: local overrides win, bundled provides the floor
4. Use merged versions in pyproject.toml
```

### Adding a Dependency

```
1. Check .claude/python-versions.md for a local pin
2. Check references/deprecated.md — is the package deprecated?
3. Check references/python.md for the recommended version
4. Check references/compatibility.md for known conflicts
```

### Docker Setup

```
1. Read references/containers.md for Python base images
2. Read references/containers.md for companion service images
3. Check .claude/python-versions.md for team-specific image preferences
```

## Version Constraint Strategy

**For Applications**:
- Use `>=` for flexibility: `fastapi>=0.115.0`
- Lock exact versions in production with `uv.lock`

**For Libraries/SDKs**:
- Use `>=` with minimum version
- Allows users flexibility in dependency trees

**For Production Deployment**:
- Use exact versions from lock file
- Ensures reproducible builds

## Critical Deprecations

Highlighted in `references/deprecated.md`:

- `python-jose` → Use `jwcrypto>=1.5.0`
- `pycrypto` → Use `cryptography>=42.0.0`
- `bitnami/*` images → Use official Docker images or managed services
- `celery` (for new projects) → Use `aio-pika>=9.4.0` + custom workers
- `pydantic` v1 → Use `pydantic>=2.9.0`

## Integration with Other Skills

This skill works with the Python scaffold plugins:

- **python-fastapi-scaffold**: Reads python.md for FastAPI stack versions, containers.md for Docker images
- **python-worker-scaffold**: Reads python.md for aio-pika/CloudEvents versions, deprecated.md for alternatives
- **python-cli-scaffold**: Reads python.md for Click/Rich versions
- **project-planning**: Consults this skill during tech stack definition

## Quick Reference

1. **"What version of X?"** → Check local overrides, then `references/python.md`
2. **"Should I use X?"** → Check `references/deprecated.md`
3. **"Why is X failing?"** → Check `references/compatibility.md`
4. **"What Docker image?"** → Read `references/containers.md`
