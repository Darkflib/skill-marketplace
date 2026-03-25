# {{PROJECT_NAME}}

{{DESCRIPTION}}

## Tech Stack

- **Python 3.12** with UV for package management
- **FastAPI** for the web framework
- **Pydantic** for configuration and validation
- **PostgreSQL** for database
- **Redis** for caching
- **Docker** for containerization

## Project Structure

```
{{PROJECT_NAME}}/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   └── config.py        # Configuration management
│   ├── models/              # Pydantic models
│   │   └── __init__.py
│   └── services/            # Business logic
│       └── __init__.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── deploy/                  # Deployment configurations
│   └── k8s/                 # Kubernetes manifests
├── scripts/                 # Utility scripts
├── pyproject.toml           # Project dependencies and configuration
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Local development environment
└── .env.example             # Environment variable template

```

## Quick Start

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose (for containerized development)

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Local Development (with Docker)

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f app
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_routes.py
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy app/
```

### Adding Dependencies

```bash
# Add a package
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update dependencies
uv sync
```

## Deployment

### Build Container Image

```bash
docker build -t {{PROJECT_NAME}}:latest .
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f deploy/k8s/

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
```

### Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/{{PROJECT_NAME}}

# Deploy to Cloud Run
gcloud run deploy {{PROJECT_NAME}} \
  --image gcr.io/PROJECT_ID/{{PROJECT_NAME}} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## API Documentation

Once running, visit `/docs` for interactive API documentation (Swagger UI) or `/redoc` for alternative documentation.

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `SECRET_KEY`: Application secret key (change in production!)
- `DEBUG`: Enable debug mode (false in production)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, WARNING, ERROR)

## License

[Your License Here]
