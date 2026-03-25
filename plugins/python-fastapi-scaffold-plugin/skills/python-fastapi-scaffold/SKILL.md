---
name: python-fastapi-scaffold
description: Scaffolds modern Python FastAPI projects with UV package management, Docker support, K8s/Cloud Run deployment templates, testing setup, and best practices. Use when starting a new Python web service, API, or microservice project. Includes complete project structure, configuration management with Pydantic, containerization, and CI/CD patterns.
---

# Python FastAPI Project Scaffold

## Overview

Provides automated scaffolding for production-ready Python FastAPI projects following modern best practices. Creates a complete project structure with UV for package management, Docker containerization, Kubernetes deployment templates, testing infrastructure, and development tooling.

## When to Use This Skill

Use this skill when:
- Starting a new Python web service or API project
- Creating a microservice for K3s or Cloud Run deployment
- Setting up a FastAPI application with modern tooling
- Implementing a project that needs containerization and K8s manifests
- Building a service that requires PostgreSQL and Redis

## Quick Start

### Using the Scaffold Script

The fastest way to create a new project:

```bash
# Navigate to where you want to create the project
cd /workspace

# Run the scaffold script
python /mnt/skills/[skill-path]/scripts/scaffold.py my-project "My API description"
```

This creates a complete project structure ready for development.

### Manual Project Creation

If you prefer to create the structure manually or customize the scaffolding:

1. Create directory structure
2. Copy template files from `/mnt/skills/[skill-path]/assets/`
3. Replace placeholders:
   - `{{PROJECT_NAME}}` → your project name
   - `{{DESCRIPTION}}` → your project description

## Project Structure

The scaffold creates the following structure:

```
my-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Pydantic settings
│   ├── models/              # Pydantic models
│   │   └── __init__.py
│   └── services/            # Business logic
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/
│   └── integration/
├── deploy/
│   └── k8s/
│       ├── deployment.yaml  # Kubernetes deployment
│       └── service.yaml     # Kubernetes service
├── scripts/                 # Utility scripts
├── pyproject.toml           # UV project configuration
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Local development environment
├── .env.example             # Environment variable template
├── .gitignore
└── README.md
```

## Technology Stack

### Core Dependencies

- **Python 3.12+**: Modern Python features and performance
- **UV**: Fast, reliable Python package management
- **FastAPI**: High-performance async web framework
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server with auto-reload

### Development Dependencies

- **pytest**: Testing framework with async support
- **pytest-cov**: Code coverage reporting
- **httpx**: HTTP client for testing FastAPI
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker

### Infrastructure

- **PostgreSQL 16**: Primary database
- **Redis 7**: Caching and session storage
- **Docker**: Containerization
- **Kubernetes**: Orchestration (K3s, K8s, Cloud Run)

## Configuration Management

### Pydantic Settings Pattern

The scaffold uses Pydantic Settings for type-safe configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "my-project"
    DEBUG: bool = False
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    SECRET_KEY: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

settings = get_settings()  # Cached singleton
```

**Benefits**:
- Type validation at startup
- Environment variable parsing
- Default values in code
- IDE autocomplete
- Validation errors prevent misconfiguration

### Environment Variables

The `.env.example` file provides a template:

```env
# Application
APP_NAME=my-project
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=change-in-production
CORS_ORIGINS=http://localhost:3000
```

## Development Workflow

### Local Development (No Docker)

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Run development server with auto-reload
uv run uvicorn app.main:app --reload

# Access the API
# http://localhost:8000       - API
# http://localhost:8000/docs  - Swagger UI
# http://localhost:8000/health - Health check
```

### Local Development (With Docker Compose)

```bash
# Start all services (app, postgres, redis)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build app
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/unit/test_routes.py

# Watch mode (requires pytest-watch)
uv run ptw
```

### Code Quality

```bash
# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy app/

# All checks (add to CI)
uv run ruff check . && \
uv run ruff format --check . && \
uv run mypy app/ && \
uv run pytest --cov=app
```

### Adding Dependencies

```bash
# Add production dependency
uv add fastapi-cache2

# Add development dependency
uv add --dev pytest-mock

# Update all dependencies
uv sync --upgrade

# Lock without installing
uv lock
```

## Containerization

### Multi-Stage Dockerfile

The scaffold includes an optimized multi-stage Dockerfile:

**Builder stage**:
- Uses official UV image for fast dependency installation
- Installs only production dependencies (`--no-dev`)
- Creates isolated virtual environment

**Production stage**:
- Minimal Python slim image
- Non-root user for security
- Health check endpoint
- Only production dependencies
- Read-only root filesystem support

### Building Images

```bash
# Build for local testing
docker build -t my-project:latest .

# Build for specific platform
docker build --platform linux/amd64 -t my-project:latest .

# Build and tag for registry
docker build -t gcr.io/project/my-project:v1.0.0 .
```

### Docker Compose

The included `docker-compose.yml` provides:
- **PostgreSQL** with health checks and persistence
- **Redis** with AOF persistence
- **App** service with proper dependencies
- **Networking** between services
- **Volume mounts** for development

## Deployment

### Kubernetes (K3s/K8s)

The scaffold includes production-ready K8s manifests:

**Deployment features**:
- 2 replicas for high availability
- Resource requests and limits
- Liveness and readiness probes
- Non-root security context
- Read-only root filesystem
- Secrets for sensitive config

**Applying manifests**:

```bash
# Create secrets first
kubectl create secret generic my-project-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=secret-key='...'

# Apply deployment and service
kubectl apply -f deploy/k8s/

# Check status
kubectl get deployments
kubectl get pods
kubectl get services
kubectl logs -l app=my-project
```

### Cloud Run

The Dockerfile is compatible with Cloud Run:

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/my-project

# Deploy to Cloud Run
gcloud run deploy my-project \
  --image gcr.io/PROJECT_ID/my-project \
  --platform managed \
  --region us-central1 \
  --set-env-vars="DATABASE_URL=postgresql://...,SECRET_KEY=..." \
  --allow-unauthenticated

# With secrets from Secret Manager
gcloud run deploy my-project \
  --image gcr.io/PROJECT_ID/my-project \
  --platform managed \
  --set-secrets="DATABASE_URL=db-url:latest,SECRET_KEY=secret-key:latest"
```

## Best Practices Implemented

### Project Structure

- **Separation of concerns**: API routes, business logic, models separate
- **Testability**: Clear boundaries for unit and integration tests
- **Modularity**: Easy to add new routers, services, models
- **Scalability**: Structure supports growth

### Configuration

- **12-Factor App**: Environment-based configuration
- **Type safety**: Pydantic validates all settings
- **Secrets management**: Never commit secrets, use env vars
- **Defaults**: Sensible defaults for development

### Security

- **Non-root containers**: Runs as UID 1000
- **Read-only filesystem**: Immutable container filesystem
- **No privilege escalation**: Security context prevents escalation
- **Secrets via env**: Sensitive data from environment/secrets
- **CORS configuration**: Explicit origin allowlist

### Development Experience

- **Fast feedback**: Auto-reload in development
- **Comprehensive tests**: Unit and integration test structure
- **Type hints**: Full type coverage for IDE support
- **Documentation**: Auto-generated API docs
- **Linting**: Consistent code style with Ruff

### Operations

- **Health checks**: /health endpoint for load balancers
- **Graceful shutdown**: Proper lifespan event handling
- **Resource limits**: CPU/memory limits prevent resource exhaustion
- **Logging**: Structured logging ready for aggregation
- **Monitoring**: Health probes for Kubernetes

## Extending the Scaffold

### Adding Database Models

Create models in `app/models/`:

```python
# app/models/user.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
```

### Adding New Routes

Create routers in `app/api/`:

```python
# app/api/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    return []
```

Include in `app/main.py`:

```python
from app.api.users import router as users_router

app.include_router(users_router)
```

### Adding Services

Create business logic in `app/services/`:

```python
# app/services/email.py
class EmailService:
    async def send_email(self, to: str, subject: str, body: str):
        # Email sending logic
        pass
```

### Adding Dependencies

For database connections, external APIs, etc.:

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(settings.DATABASE_URL)

async def get_db():
    async with AsyncSession(engine) as session:
        yield session
```

Use in routes:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    # Use db session
    pass
```

## Customization Guide

### Removing PostgreSQL/Redis

If you don't need these services:

1. Remove from `docker-compose.yml`
2. Remove from `pyproject.toml` dependencies
3. Update `.env.example` to remove DB/Redis vars
4. Simplify `app/core/config.py` settings

### Adding Background Tasks

For job queues, schedulers, workers:

1. Add dependency: `uv add celery` or `uv add arq`
2. Create `app/workers/` directory
3. Add worker code and Dockerfile
4. Update `docker-compose.yml` with worker service
5. Add K8s Deployment for worker

### Adding Authentication

For JWT, OAuth2, etc.:

1. Add dependency: `uv add python-jose[cryptography] passlib[bcrypt]`
2. Create `app/core/security.py` for auth logic
3. Add dependencies to routes requiring auth
4. Update models for User, Token, etc.

## Common Patterns

### Dependency Injection

FastAPI's dependency injection for reusable components:

```python
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token and return user
    return user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Background Tasks

For tasks that don't need immediate execution:

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email
    pass

@router.post("/send")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "notification")
    return {"message": "Email will be sent"}
```

### Middleware

For request/response processing:

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Error Handling

Custom exception handlers:

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )
```

## Troubleshooting

### UV sync fails

```bash
# Clear cache and retry
uv cache clean
uv sync
```

### Port already in use

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uv run uvicorn app.main:app --port 8001
```

### Docker build fails

```bash
# Check Docker is running
docker ps

# Clean build cache
docker builder prune

# Build with verbose output
docker build --progress=plain -t my-project .
```

### Tests failing

```bash
# Run with verbose output
uv run pytest -vv

# Run specific test
uv run pytest tests/unit/test_routes.py::test_get_item -vv

# Debug with pdb
uv run pytest --pdb
```

## Migration from Requirements.txt

If converting an existing project to UV:

```bash
# Import from requirements.txt
uv add -r requirements.txt

# Or let UV detect dependencies
uv init

# Verify pyproject.toml
cat pyproject.toml
```

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **UV Documentation**: https://github.com/astral-sh/uv
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Kubernetes Patterns**: https://kubernetes.io/docs/concepts/

## Summary

This scaffold provides:
- ✅ Modern Python 3.12+ project structure
- ✅ UV for fast, reliable dependency management
- ✅ FastAPI with async support and auto-docs
- ✅ Pydantic for type-safe configuration
- ✅ Docker multi-stage builds for production
- ✅ Docker Compose for local development
- ✅ Kubernetes manifests for deployment
- ✅ Testing infrastructure with pytest
- ✅ Code quality tools (ruff, mypy)
- ✅ Security best practices
- ✅ Health checks and monitoring

Use the scaffold script for instant project setup, then customize based on your specific requirements.
