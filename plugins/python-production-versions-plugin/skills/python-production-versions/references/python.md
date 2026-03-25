# Python Production Library Versions

**Last Updated**: 2025-11-15  
**Python Version**: 3.12+

This is the authoritative reference for Python library versions used in production. When creating new projects or updating dependencies, always use these versions unless there's a specific reason documented elsewhere.

---

## Package Management

- **UV**: Latest stable (recommended for all new projects)
  - Fast, reliable Python package management
  - Replaces pip, pip-tools, virtualenv, poetry
  - Use for: all new Python projects

---

## Web Frameworks

### FastAPI
- **Version**: `>=0.115.0`
- **Companion**: `uvicorn[standard]>=0.32.0`
- **Notes**:
  - v0.100.0+ has new exception handler structure
  - Use `pydantic>=2.9.0` (required)
  - Default to async route handlers
- **Example**:
  ```toml
  fastapi = ">=0.115.0"
  uvicorn = {extras = ["standard"], version = ">=0.32.0"}
  ```

### Flask
- **Version**: `>=3.0.0`
- **Notes**:
  - Flask 2.x is EOL - always use 3.x
  - For new projects, prefer FastAPI unless specific Flask ecosystem requirements

---

## Data Validation & Configuration

### Pydantic
- **Version**: `>=2.9.0`
- **Settings**: `pydantic-settings>=2.6.0`
- **CRITICAL NOTES**:
  - Pydantic v2 is **NOT** backward compatible with v1
  - v1 is deprecated - always use v2 for new projects
  - Major changes in v2:
    - `Config` class → `model_config` dict
    - `@validator` → `@field_validator`
    - `.dict()` → `.model_dump()`
    - `.parse_obj()` → `.model_validate()`
- **Example**:
  ```toml
  pydantic = ">=2.9.0"
  pydantic-settings = ">=2.6.0"
  ```

### python-dotenv
- **Version**: `>=1.0.0`
- **Usage**: Development only
- **Notes**:
  - Use for local `.env` file loading
  - In production, use Pydantic Settings with direct environment variables
  - Don't use for production configuration

---

## Message Queues & Task Processing

### RabbitMQ Client
- **Version**: `aio-pika>=9.4.0`
- **Notes**:
  - Use aio-pika for async (preferred)
  - Do NOT use `pika` directly (sync only)
  - Breaking changes in v9.0 - connection interface changed
  - Robust reconnection built-in
- **Example**:
  ```toml
  aio-pika = ">=9.4.0"
  ```

### Task Queue Alternatives
- **dramatiq**: Not recommended for our use case
  - Reason: Requires too much abstraction for CloudEvents + RabbitMQ direct control
  - Alternative: Use aio-pika with custom consumer pattern (see worker scaffold)
- **Celery**: Not recommended for new projects
  - Reason: Heavy, complex, RabbitMQ + Redis required
  - Alternative: Use aio-pika for event-driven, APScheduler for periodic tasks

---

## Event Handling

### CloudEvents
- **Version**: `cloudevents>=1.11.0`
- **Signing**: `jwcrypto>=1.5.0`
- **Notes**:
  - Standard event format for microservices
  - Use JWS (RS256) for message signing
  - See worker scaffold for CloudEvent handler implementation
- **Example**:
  ```toml
  cloudevents = ">=1.11.0"
  jwcrypto = ">=1.5.0"
  ```

---

## Logging

### structlog
- **Version**: `>=24.4.0`
- **Notes**:
  - Use for structured JSONL logging in all services
  - Consistent across API, workers, and CLI tools
  - Better for log aggregation (ELK, Loki, etc.)
- **Example**:
  ```toml
  structlog = ">=24.4.0"
  ```

---

## CLI Tools

### Click
- **Version**: `>=8.1.0`
- **Rich (for output)**: `>=13.9.0`
- **Notes**:
  - Click for command framework
  - Rich for beautiful terminal output (tables, progress bars, colors)
  - Use together for production CLI tools
- **Example**:
  ```toml
  click = ">=8.1.0"
  rich = ">=13.9.0"
  ```

---

## Database

### PostgreSQL Drivers
- **Sync (psycopg)**: `psycopg[binary]>=3.2.0` or `psycopg2-binary>=2.9.9`
- **Async (asyncpg)**: `asyncpg>=0.29.0`
- **Notes**:
  - psycopg 3.x is the new default (supports both sync and async)
  - For FastAPI/async apps, use asyncpg or psycopg 3 async mode
  - psycopg2 is legacy but still widely used

### SQLAlchemy
- **Version**: `>=2.0.0`
- **Async**: Requires `asyncpg>=0.29.0` or async-compatible driver
- **Migrations**: `alembic>=1.13.0` (required for SQLAlchemy 2.x)
- **Notes**:
  - SQLAlchemy 2.0 has breaking changes from 1.4
  - Use 2.0 style syntax (avoid legacy patterns)
- **Example**:
  ```toml
  sqlalchemy = ">=2.0.0"
  alembic = ">=1.13.0"
  asyncpg = ">=0.29.0"
  ```

---

## Redis

### Redis Client
- **Sync**: `redis>=5.0.0`
- **Async**: `redis[hiredis]>=5.0.0` (with hiredis for performance)
- **Notes**:
  - v5.0+ unified sync and async interfaces
  - Use hiredis for better performance
  - Redis Streams support built-in
- **Example**:
  ```toml
  redis = {extras = ["hiredis"], version = ">=5.0.0"}
  ```

---

## HTTP Clients

### httpx
- **Version**: `>=0.27.0`
- **Notes**:
  - Modern replacement for requests
  - Supports async natively
  - Use for FastAPI testing and external API calls
  - Has better typing than requests
- **Example**:
  ```toml
  httpx = ">=0.27.0"
  ```

### requests
- **Version**: `>=2.32.0`
- **Notes**:
  - Still fine for sync-only scripts
  - For new async code, prefer httpx
  - Widely used and stable

---

## Scheduling

### APScheduler
- **Version**: `>=3.10.0`
- **Notes**:
  - Use for periodic tasks, cron-like scheduling
  - Integrates well with FastAPI (use lifespan events)
  - Alternative to Celery Beat for simpler use cases
- **Example**:
  ```toml
  apscheduler = ">=3.10.0"
  ```

---

## Testing

### pytest
- **Version**: `>=8.3.0`
- **Async support**: `pytest-asyncio>=0.24.0`
- **Coverage**: `pytest-cov>=6.0.0`
- **Mocking**: `pytest-mock>=3.14.0`
- **Example**:
  ```toml
  [project.optional-dependencies]
  dev = [
      "pytest>=8.3.0",
      "pytest-asyncio>=0.24.0",
      "pytest-cov>=6.0.0",
      "pytest-mock>=3.14.0",
  ]
  ```

---

## Code Quality

### Ruff
- **Version**: `>=0.7.0`
- **Notes**:
  - Replaces: black, isort, flake8, pylint
  - Fast Rust-based linter and formatter
  - Use for all new Python projects
- **Example**:
  ```toml
  ruff = ">=0.7.0"
  ```

### mypy
- **Version**: `>=1.13.0`
- **Notes**:
  - Static type checker
  - Use with `strict = true` for new projects
  - Catches many bugs at development time
- **Example**:
  ```toml
  mypy = ">=1.13.0"
  ```

---

## Common Combinations

### Web API Stack
```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "redis[hiredis]>=5.0.0",
    "structlog>=24.4.0",
    "httpx>=0.27.0",
]
```

### Worker Stack
```toml
[project]
dependencies = [
    "aio-pika>=9.4.0",
    "cloudevents>=1.11.0",
    "jwcrypto>=1.5.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "structlog>=24.4.0",
]
```

### CLI Tool Stack
```toml
[project]
dependencies = [
    "click>=8.1.0",
    "rich>=13.9.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "structlog>=24.4.0",
]
```

---

## Version Constraint Strategy

### For Applications
- Use `>=` for flexibility: `fastapi>=0.115.0`
- Lock exact versions in CI/CD with `uv.lock`

### For Libraries/SDKs
- Use `>=` with minimum version: `fastapi>=0.115.0`
- Allows users flexibility in their dependency trees

### For Production Deployment
- Use exact versions from `uv.lock`
- Ensures reproducible builds

---

## Automation Notes

This file can be automatically updated by checking:
- PyPI latest versions
- Breaking change announcements
- Security advisories
- Team decisions documented in PRs/issues

**Suggested automation**:
```bash
# Check for updates
uv pip list --outdated

# Update this file with new versions
# Review breaking changes before updating
```
