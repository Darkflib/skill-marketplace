# Container Images & Base Images

**Last Updated**: 2025-11-15

Recommended Docker base images and container configurations for production use.

---

## Python Base Images

### Recommended Images

| Image | Size | Use Case | Security Updates |
|-------|------|----------|------------------|
| `python:3.12-slim` | ~180MB | **Recommended for most apps** | ✅ Official, regular updates |
| `python:3.12-alpine` | ~50MB | Size-critical deployments | ✅ Official, but fewer binary wheels |
| `python:3.12` | ~1GB | Development/testing only | ✅ Official, includes build tools |
| `cgr.dev/chainguard/python:latest` | ~60MB | Security-focused | ✅ Daily automated rebuilds |

**Default Choice**: `python:3.12-slim`
- Good balance of size and compatibility
- Has most common libraries pre-installed
- Works with most Python packages

**Example Dockerfile**:
```dockerfile
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install runtime dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Rest of Dockerfile...
```

---

## Infrastructure Service Images

### PostgreSQL

| Image | Notes |
|-------|-------|
| `postgres:16-alpine` | **Recommended** - Official, lightweight |
| `postgres:16` | Official, Debian-based (larger) |
| ~~`bitnami/postgresql`~~ | ❌ Free tier discontinued Sept 2025 |

**Recommendation**: Use `postgres:16-alpine` or managed database (AWS RDS, GCP Cloud SQL, etc.)

**Example**:
```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

---

### Redis

| Image | Notes |
|-------|-------|
| `redis:7-alpine` | **Recommended** - Official, lightweight |
| `redis:7` | Official, Debian-based |
| ~~`bitnami/redis`~~ | ❌ Free tier discontinued Sept 2025 |

**Recommendation**: Use `redis:7-alpine` or managed Redis (AWS ElastiCache, GCP Memorystore, etc.)

**Example**:
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
```

---

### RabbitMQ

| Image | Notes |
|-------|-------|
| `rabbitmq:3.13-management-alpine` | **Recommended** - Includes management UI |
| `rabbitmq:3.13-alpine` | Smaller, no management UI |
| ~~`bitnami/rabbitmq`~~ | ❌ Free tier discontinued Sept 2025 |

**Recommendation**: Use official `rabbitmq:3.13-management-alpine`

**Example**:
```yaml
rabbitmq:
  image: rabbitmq:3.13-management-alpine
  environment:
    RABBITMQ_DEFAULT_USER: ${RABBIT_USER}
    RABBITMQ_DEFAULT_PASS: ${RABBIT_PASS}
  ports:
    - "5672:5672"    # AMQP
    - "15672:15672"  # Management UI
```

---

### Nginx

| Image | Notes |
|-------|-------|
| `nginx:alpine` | **Recommended** - Official, minimal |
| `nginx:latest` | Official, Debian-based |

**Example**:
```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

---

## Base Image Comparisons

### Python Image Sizes

```
python:3.12         → 1.02 GB  (full, has build tools)
python:3.12-slim    → 181 MB   ✅ Recommended
python:3.12-alpine  → 51 MB    (smaller, fewer wheels)
chainguard/python   → 60 MB    (security-focused)
```

### When to Use Alpine

**Use Alpine if**:
- ✅ Image size is critical (embedded, edge computing)
- ✅ Security minimalism is required
- ✅ You're not using packages with C extensions

**Avoid Alpine if**:
- ❌ You need packages with compiled extensions (numpy, pandas, etc.)
- ❌ Build times are important (compiling from source is slow)
- ❌ You're new to Docker (Debian/Ubuntu more familiar)

**Common Alpine Issues**:
```dockerfile
# ❌ This fails on Alpine
RUN pip install numpy pandas

# ✅ This works but is slow (compiles from source)
RUN apk add --no-cache gcc musl-dev && \
    pip install numpy pandas
```

---

## Multi-Architecture Builds

For deploying to both AMD64 (x86_64) and ARM64 (AWS Graviton, Raspberry Pi):

```dockerfile
FROM python:3.12-slim

# These images support both amd64 and arm64
# Docker will automatically pull the right architecture
```

**Building multi-arch images**:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .
```

---

## Security Best Practices

### Non-Root User

```dockerfile
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# ... install dependencies ...

# Switch to non-root user
USER appuser

CMD ["python", "app.py"]
```

### Read-Only Root Filesystem

```dockerfile
# In Dockerfile
USER appuser

# In Kubernetes
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
```

### Minimal Layers

```dockerfile
# ❌ Multiple layers
RUN apt-get update
RUN apt-get install -y ca-certificates
RUN rm -rf /var/lib/apt/lists/*

# ✅ Single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*
```

---

## Image Scanning

**Tools**:
- **Trivy**: `docker run aquasec/trivy image myapp:latest`
- **Snyk**: `snyk container test myapp:latest`
- **Docker Scout**: `docker scout cves myapp:latest`

**In CI/CD**:
```yaml
# GitHub Actions example
- name: Scan image
  run: |
    docker run --rm \
      -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image --severity HIGH,CRITICAL myapp:latest
```

---

## Registry Recommendations

| Registry | Use Case | Notes |
|----------|----------|-------|
| Docker Hub | Public images | Rate limits on free tier |
| GitHub Container Registry (ghcr.io) | Private/public images | Free for public repos |
| Google Container Registry (gcr.io) | GCP deployments | Pay for storage |
| AWS ECR | AWS deployments | Pay for storage |
| Azure Container Registry | Azure deployments | Pay for storage |

**For production**: Use private registry (ghcr.io, gcr.io, ECR, ACR)

---

## Bitnami Migration Guide

Since Bitnami discontinued free tier (Sept 2025):

### PostgreSQL
```yaml
# ❌ OLD
image: bitnami/postgresql:16

# ✅ NEW
image: postgres:16-alpine
# Or use managed service (RDS, Cloud SQL)
```

### Redis
```yaml
# ❌ OLD
image: bitnami/redis:7

# ✅ NEW
image: redis:7-alpine
# Or use managed service (ElastiCache, Memorystore)
```

### RabbitMQ
```yaml
# ❌ OLD
image: bitnami/rabbitmq:3.13

# ✅ NEW
image: rabbitmq:3.13-management-alpine
```

### Kafka
```yaml
# ❌ OLD
image: bitnami/kafka

# ✅ NEW
image: confluentinc/cp-kafka:latest
# Or use Strimzi operator on Kubernetes
# Or use managed service (MSK, Confluent Cloud)
```

---

## Helm Chart Alternatives

Since Bitnami Helm charts moved to paid tier:

| Service | Alternative |
|---------|-------------|
| PostgreSQL | Use managed DB or official postgres Docker image |
| Redis | Use managed Redis or official redis image |
| RabbitMQ | Official rabbitmq image + StatefulSet |
| Kafka | Strimzi Operator or Confluent Operator |
| Nginx | Nginx Ingress Controller (official) |

**Operators** (Kubernetes-native):
- **Strimzi**: Kafka operator (free, open source)
- **CloudNativePG**: PostgreSQL operator
- **Redis Operator**: by Opstree or Spotahome

---

## Image Update Strategy

### Pinning Strategy

```dockerfile
# ❌ Don't use 'latest' in production
FROM python:latest

# ✅ Pin major.minor
FROM python:3.12-slim

# ✅ Pin exact version for reproducibility
FROM python:3.12.7-slim

# ✅ Pin by digest for maximum security
FROM python:3.12-slim@sha256:abc123...
```

**Recommendation**:
- **Development**: Pin major.minor (`3.12-slim`)
- **Production**: Pin exact version (`3.12.7-slim`) or digest

### Automated Updates

```yaml
# Dependabot config (.github/dependabot.yml)
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Quick Reference

**Default Choices for New Projects**:
```dockerfile
# Python app
FROM python:3.12-slim

# PostgreSQL
FROM postgres:16-alpine

# Redis  
FROM redis:7-alpine

# RabbitMQ
FROM rabbitmq:3.13-management-alpine

# Nginx
FROM nginx:alpine
```

These are all:
- ✅ Official Docker images
- ✅ Actively maintained
- ✅ Regular security updates
- ✅ Well documented
- ✅ Free and open source
