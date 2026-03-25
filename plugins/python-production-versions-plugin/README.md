# Python Production Versions - Maintenance Guide

This plugin provides the authoritative reference for Python library versions used in production. It provides version floors that can be supplemented by project-local overrides. It requires periodic updates to stay current.

## Local Overrides

Teams can create `.claude/python-versions.md` in their project root to override or supplement the bundled references. See the SKILL.md for the override format.

## File Structure

```
skills/python-production-versions/
├── SKILL.md                    # Skill description, usage, and override mechanism
└── references/
    ├── python.md               # Python library versions (update most often)
    ├── deprecated.md           # Deprecated packages and replacements
    ├── compatibility.md        # Known version conflicts
    └── containers.md           # Docker base images for Python services
```

## What to Update and When

### Weekly/Monthly: `references/python.md`

**Check for**:
- Security updates on critical packages (FastAPI, Pydantic, etc.)
- New major/minor versions of commonly used libraries
- Breaking changes in recent releases

**How to check**:
```bash
# In a project using these packages
uv pip list --outdated

# Or check PyPI directly for specific packages
# https://pypi.org/project/fastapi/
# https://pypi.org/project/pydantic/
```

**Update process**:
1. Check release notes for breaking changes
2. Update version numbers in `python.md`
3. Add any breaking change notes to the package section
4. Update "Last Updated" date at top of file

### As-Needed: `references/deprecated.md`

Add entries when:
- A library is unmaintained or deprecated
- A better alternative emerges
- Security vulnerabilities are found

### As-Needed: `references/compatibility.md`

Add entries when:
- You encounter a version conflict
- A specific package combination causes issues
- Platform-specific problems arise (Apple Silicon, ARM, etc.)

### As-Needed: `references/containers.md`

Update when:
- New Docker base image versions are released
- Security advisories for container images
- Image deprecations announced

## Automation

### Version Checking Script

```python
#!/usr/bin/env python3
"""Check for outdated package versions in skill references."""

import re
import requests
from packaging import version

def get_latest_version(package_name):
    """Get latest version from PyPI."""
    resp = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    return resp.json()["info"]["version"]

def parse_versions_from_file(filepath):
    """Extract package versions from markdown file."""
    with open(filepath) as f:
        content = f.read()
    pattern = r'`(\w+(?:-\w+)*)(?:>=|==)(\d+\.\d+(?:\.\d+)?)'
    matches = re.findall(pattern, content)
    return {pkg: ver for pkg, ver in matches}

def check_outdated():
    """Check which packages have newer versions."""
    current = parse_versions_from_file(
        "skills/production-library-versions/references/python.md"
    )
    for pkg, current_ver in current.items():
        try:
            latest = get_latest_version(pkg)
            if version.parse(latest) > version.parse(current_ver):
                print(f"  {pkg}: {current_ver} -> {latest}")
        except Exception as e:
            print(f"  Error checking {pkg}: {e}")

if __name__ == "__main__":
    check_outdated()
```

### CI Workflow

```yaml
# .github/workflows/update-versions.yml
name: Check Library Versions

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for package updates
        run: python scripts/check_versions.py
      - name: Create PR if updates found
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Update library versions"
          body: "Automated update of package versions"
          branch: update-library-versions
```

## Review Checklist

Run monthly:

- [ ] Check FastAPI, Pydantic, SQLAlchemy, aio-pika latest versions
- [ ] Review security advisories (GitHub, Snyk)
- [ ] Search for newly deprecated packages
- [ ] Review recent GitHub issues for version conflicts
- [ ] Check Docker Hub for new official image versions
- [ ] Update "Last Updated" dates in reference files

## Sources to Monitor

- **PyPI**: https://pypi.org/
- **Python.org**: https://www.python.org/downloads/
- **Docker Hub**: https://hub.docker.com/
- **GitHub Security Advisories**: https://github.com/advisories
- **Snyk Vulnerability Database**: https://security.snyk.io/
