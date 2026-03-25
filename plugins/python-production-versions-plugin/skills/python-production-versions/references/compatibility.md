# Library Compatibility & Known Issues

**Last Updated**: 2025-11-15

This document tracks known compatibility issues, version conflicts, and workarounds. Check this before debugging mysterious dependency errors.

---

## Known Version Conflicts

### SQLAlchemy + Alembic
- **Issue**: `sqlalchemy>=2.0` + `alembic<1.13` = incompatible
- **Solution**: Always use `alembic>=1.13.0` with SQLAlchemy 2.0
- **Error Message**: `AttributeError: 'Engine' object has no attribute 'execute'`

```toml
# ✅ Correct
sqlalchemy = ">=2.0.0"
alembic = ">=1.13.0"

# ❌ Breaks
sqlalchemy = ">=2.0.0"
alembic = "1.12.0"  # Too old!
```

---

### Pydantic + FastAPI
- **Issue**: FastAPI <0.100 doesn't fully support Pydantic v2
- **Solution**: Use `fastapi>=0.100.0` with `pydantic>=2.0.0`
- **Note**: FastAPI 0.100+ is designed for Pydantic v2

```toml
# ✅ Correct
fastapi = ">=0.115.0"
pydantic = ">=2.9.0"

# ❌ May have issues
fastapi = "0.95.0"  # Too old for Pydantic v2
pydantic = ">=2.0.0"
```

---

### aio-pika + aiormq
- **Issue**: aio-pika 9.x requires compatible aiormq version
- **Solution**: Let UV/pip resolve automatically, or pin both:
  ```toml
  aio-pika = ">=9.4.0"
  # aiormq will be resolved automatically
  ```
- **Note**: Don't manually pin aiormq unless debugging

---

### uvicorn + httptools
- **Issue**: uvicorn[standard] includes httptools, conflicts if installed separately
- **Solution**: Use `uvicorn[standard]` extra, don't install httptools manually
- **Correct**:
  ```toml
  uvicorn = {extras = ["standard"], version = ">=0.32.0"}
  ```

---

### pytest + pytest-asyncio
- **Issue**: pytest-asyncio <0.23 has issues with pytest 8.x
- **Solution**: Use `pytest-asyncio>=0.24.0` with `pytest>=8.0.0`
- **Error**: `RuntimeWarning: coroutine was never awaited`

```toml
# ✅ Correct
pytest = ">=8.3.0"
pytest-asyncio = ">=0.24.0"
```

---

## Platform-Specific Issues

### macOS ARM (M1/M2/M3)
- **psycopg2**: Binary wheels don't always work
  - **Solution**: Use `psycopg2-binary` or `psycopg>=3.0` (native ARM support)
  - **Alternative**: Install PostgreSQL via Homebrew first

- **grpcio**: May need XCode command line tools
  - **Solution**: `xcode-select --install`

- **cryptography**: Needs OpenSSL from Homebrew
  - **Solution**: `brew install openssl` then reinstall cryptography

---

### Linux ARM (Raspberry Pi, AWS Graviton)
- **numpy/pandas**: Binary wheels may not exist
  - **Solution**: Install system packages first: `apt install python3-numpy python3-pandas`
  - **Alternative**: Use Docker with pre-built images

---

### Windows
- **aio-pika/asyncio**: Event loop issues with ProactorEventLoop
  - **Solution**: Use `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())`
  
- **cryptography**: Needs Visual C++ Build Tools
  - **Solution**: Install Visual Studio Build Tools

---

## Python Version Compatibility

### Python 3.12 Changes
- **Removed**: `distutils` (use `setuptools` instead)
- **Changed**: `datetime.utcnow()` deprecated → use `datetime.now(timezone.utc)`
- **Impact**: Some older packages may not work

**Packages that work well with 3.12**:
- ✅ FastAPI
- ✅ Pydantic v2
- ✅ SQLAlchemy 2.x
- ✅ Click
- ✅ All our standard stack

**Packages with 3.12 issues** (as of 2025-11):
- ⚠️ Some old Jupyter extensions (upgrade Jupyter)

---

### Python 3.13 New Features (Nov 2024)
- **Free-threaded mode** (experimental, opt-in)
- **JIT compiler** (experimental)
- **Impact**: Most packages work, but check compatibility for cutting-edge features

**Status**: Use 3.13 for development, but 3.12 is recommended for production (more stable ecosystem).

---

## Docker Image Compatibility

### Multi-architecture Builds
When building for both `amd64` and `arm64`:

```dockerfile
# ✅ Works on both
FROM python:3.12-slim

# ❌ May have issues
FROM python:3.12-alpine  # Some packages don't have musl wheels
```

**Alpine Issues**:
- No binary wheels for many packages (longer build times)
- Some packages need `gcc`, `musl-dev`, etc.
- Prefer `-slim` over `-alpine` unless you need the smaller size

---

## Database Driver Compatibility

### PostgreSQL Version Matrix

| Driver | PostgreSQL 12 | PostgreSQL 13 | PostgreSQL 14 | PostgreSQL 15 | PostgreSQL 16 |
|--------|--------------|--------------|--------------|--------------|--------------|
| `psycopg2>=2.9` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `psycopg>=3.2` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `asyncpg>=0.29` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Recommendation**: Use PostgreSQL 15 or 16 for new deployments.

---

### Redis Version Matrix

| Driver | Redis 6 | Redis 7 |
|--------|---------|---------|
| `redis>=5.0` | ✅ | ✅ |
| `aioredis` (deprecated) | ✅ | ⚠️ Use `redis[hiredis]` instead |

**Note**: `aioredis` is merged into `redis>=4.2.0` - just use `redis` package for both sync and async.

---

## Common Error Messages & Fixes

### "No module named '_bz2'"
- **Cause**: Python compiled without bz2 support
- **Fix** (Ubuntu/Debian): `apt install libbz2-dev` then recompile Python
- **Fix** (macOS): `brew install bzip2` then reinstall Python

### "Symbol not found: _SSL_library_init"
- **Cause**: OpenSSL version mismatch
- **Fix**: Reinstall Python with correct OpenSSL version
- **macOS**: `brew reinstall python@3.12`

### "ImportError: cannot import name 'soft_unicode' from 'markupsafe'"
- **Cause**: Jinja2/MarkupSafe version conflict
- **Fix**: `uv sync --upgrade`

### "asyncio RuntimeWarning: coroutine was never awaited"
- **Cause**: Calling async function without `await`
- **Fix**: Ensure all async functions are awaited or used with `asyncio.create_task()`

### "sqlalchemy.exc.ArgumentError: Mapper mapped class X has no property 'Y'"
- **Cause**: SQLAlchemy 1.x code running on 2.x
- **Fix**: Update to SQLAlchemy 2.0 syntax or use compatibility mode

---

## Integration Compatibility

### FastAPI + SQLAlchemy + Alembic
**Working Stack**:
```toml
fastapi = ">=0.115.0"
sqlalchemy = ">=2.0.0"
alembic = ">=1.13.0"
asyncpg = ">=0.29.0"  # For async
```

**Async Session Pattern**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...")

async def get_db():
    async with AsyncSession(engine) as session:
        yield session
```

---

### FastAPI + Pydantic v2 + SQLAlchemy
**Issue**: Pydantic v2 changed `.dict()` to `.model_dump()`
**Fix**: Use Pydantic v2 syntax throughout:

```python
# ❌ Pydantic v1 syntax
data = user.dict()

# ✅ Pydantic v2 syntax
data = user.model_dump()
```

---

### RabbitMQ + CloudEvents + JWS
**Working Stack**:
```toml
aio-pika = ">=9.4.0"
cloudevents = ">=1.11.0"
jwcrypto = ">=1.5.0"
```

**Note**: Don't use `python-jose` - it's unmaintained. See `deprecated.md`.

---

## Testing Compatibility

### pytest + FastAPI + async
**Working Stack**:
```toml
pytest = ">=8.3.0"
pytest-asyncio = ">=0.24.0"
httpx = ">=0.27.0"  # For testing FastAPI
```

**Test Configuration**:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Important for pytest-asyncio 0.23+
```

---

## Workarounds for Common Issues

### Issue: UV can't resolve dependencies
**Symptom**: `Unable to find a version of X compatible with Y`
**Workarounds**:
1. Check for outdated version constraints in `pyproject.toml`
2. Run `uv sync --upgrade` to get latest compatible versions
3. Check this compatibility guide for known conflicts
4. Manually pin conflicting package to compatible version

### Issue: Import errors after dependency update
**Symptom**: `ImportError` or `AttributeError` after updating packages
**Workarounds**:
1. Check release notes for breaking changes
2. Review this compatibility guide
3. Check `deprecated.md` for replacement libraries
4. Lock to previous working version temporarily

---

## Monitoring Compatibility

**Automation ideas**:

```bash
# Check for known incompatible combinations
rg "sqlalchemy.*2\\.0" pyproject.toml && rg "alembic.*1\\.(10|11|12)" pyproject.toml
# If both match, flag for review

# Check for deprecated packages
rg "python-jose|pycrypto" pyproject.toml
# Alert if found
```

**Regular review**:
- Update this file when encountering new conflicts
- Check upstream issue trackers for compatibility notes
- Test version updates in staging before production
