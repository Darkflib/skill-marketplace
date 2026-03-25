# Multi-stage build for Python CLI tool
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r cliuser && useradd -r -g cliuser cliuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app/ /app/app/

# Set ownership
RUN chown -R cliuser:cliuser /app

# Switch to non-root user
USER cliuser

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set CLI as entrypoint
ENTRYPOINT ["{{PROJECT_NAME}}"]
CMD ["--help"]
