---
name: python-worker-scaffold
description: Scaffolds Python background worker projects for processing RabbitMQ messages with signed CloudEvents. Use when creating workers, message processors, async task handlers, or event-driven microservices. Includes RabbitMQ consumption, CloudEvent signing/verification with JWS, structured JSONL logging, Docker support, K8s manifests, retry logic, and dead letter queues.
---

# Python Worker Scaffold

## Overview

Provides automated scaffolding for production-ready Python background workers that consume messages from RabbitMQ. Workers process signed CloudEvents with automatic signature verification, retry logic, and dead letter queue handling. Includes structured JSONL logging, Docker containerization, and Kubernetes deployment templates.

## When to Use This Skill

Use this skill when:
- Creating background workers for async task processing
- Building event-driven microservices
- Processing messages from RabbitMQ queues
- Implementing event handlers for CloudEvents
- Setting up workers for K3s or Cloud Run deployment
- Building distributed systems with message-based communication

## Quick Start

### Using the Scaffold Script

```bash
# Create a new worker project
python /mnt/skills/[skill-path]/scripts/scaffold.py order-processor "Process order events"
```

This creates a complete worker structure ready for customization.

## Project Structure

The scaffold creates:

```
order-processor/
├── app/
│   ├── main.py                      # Worker entry point
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── message_consumer.py      # RabbitMQ message consumer
│   ├── handlers/                    # Business logic
│   │   ├── __init__.py
│   │   └── example_handler.py
│   └── core/
│       ├── __init__.py
│       ├── config.py                # Pydantic settings
│       ├── logging.py               # Structured logging
│       ├── cloudevents.py           # CloudEvent signing/verification
│       └── rabbitmq.py              # RabbitMQ connection management
├── tests/
│   ├── __init__.py
│   └── test_handlers.py
├── deploy/k8s/
│   └── deployment.yaml
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Technology Stack

### Core Dependencies

- **Python 3.12+**: Modern Python with async support
- **aio-pika**: Async RabbitMQ client
- **CloudEvents**: Standard event format
- **jwcrypto**: JWS signing for CloudEvents (RS256)
- **structlog**: Structured JSONL logging
- **Pydantic**: Configuration management

### Development Dependencies

- **pytest**: Testing with async support
- **pytest-mock**: Mocking for tests
- **ruff**: Linting and formatting
- **mypy**: Static type checking

### Infrastructure

- **RabbitMQ**: Message broker
- **Docker**: Containerization
- **Kubernetes**: Orchestration

## Architecture

### Message Flow

```
RabbitMQ Queue
    ↓
[JWS-signed CloudEvent]
    ↓
Worker receives message
    ↓
Verify JWS signature
    ↓
Extract CloudEvent
    ↓
Dispatch to handler (by event type)
    ↓
Execute business logic
    ↓
ACK message (success) or REJECT (failure)
```

### CloudEvents with JWS

Messages are CloudEvents wrapped in JSON Web Signatures:

**CloudEvent structure**:
```json
{
  "specversion": "1.0",
  "type": "com.example.order.created",
  "source": "https://example.com/orders",
  "id": "a12b34c5-...",
  "time": "2025-01-01T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "orderId": "12345",
    "amount": 99.99
  }
}
```

**JWS envelope** (what's actually sent):
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzcGVjdmVyc2lvbiI6I...
```

The worker:
1. Receives JWS token from queue
2. Verifies signature using public key
3. Extracts CloudEvent if valid
4. Routes to appropriate handler
5. ACKs message on success

### Error Handling

**Retry Logic**:
- Failed messages are retried up to `MAX_RETRIES` (default: 3)
- Configurable retry delay
- Retry count tracked in message headers

**Dead Letter Queue**:
- After max retries, messages go to DLQ
- Format: `{queue_name}.dlq`
- Allows manual inspection and reprocessing

**Invalid Signatures**:
- Immediately rejected (no retry)
- Sent to DLQ for investigation

## Setup and Configuration

### Generate CloudEvents Keys

```bash
# Generate RSA key pair
ssh-keygen -t rsa -b 2048 -m PEM -f cloudevents_key

# Convert public key to PEM format
ssh-keygen -f cloudevents_key.pub -e -m PEM > cloudevents_key_public.pem
```

### Environment Configuration

The `.env.example` template includes:

```env
# Worker
WORKER_NAME=order-processor
LOG_LEVEL=INFO

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672/
QUEUE_NAME=orders_queue
PREFETCH_COUNT=10

# CloudEvents (paste full PEM keys)
CLOUDEVENTS_SIGNING_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
CLOUDEVENTS_VERIFICATION_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Retry behavior
MAX_RETRIES=3
RETRY_DELAY=60
```

## Development Workflow

### Local Development with Docker

```bash
# Configure environment
cp .env.example .env
# Add your CloudEvents keys to .env

# Start RabbitMQ and worker
docker-compose up -d

# View worker logs
docker-compose logs -f worker

# Access RabbitMQ management UI
# http://localhost:15672 (guest/guest)
```

### Local Development without Docker

```bash
# Install dependencies
uv sync

# Start RabbitMQ
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.13-management-alpine

# Update .env with localhost URLs
# RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Run worker
uv run python -m app.main
```

### Adding Event Handlers

1. **Create handler function**:

```python
# app/handlers/order_handler.py
import structlog
from cloudevents.http import CloudEvent

logger = structlog.get_logger()

async def handle_order_created(event: CloudEvent) -> None:
    """Process order created event."""
    data = event.get_data()
    order_id = data.get("orderId")
    
    logger.info("Processing order", order_id=order_id)
    
    # Your business logic here:
    # - Update database
    # - Send notification
    # - Call external API
    # - Publish new events
    
    logger.info("Order processed", order_id=order_id)
```

2. **Register handler**:

```python
# app/consumers/message_consumer.py
from app.handlers.order_handler import handle_order_created

class MessageConsumer:
    def __init__(self, ce_handler: CloudEventHandler):
        self.ce_handler = ce_handler
        
        # Map event types to handlers
        self.handlers = {
            "com.example.order.created": handle_order_created,
            # Add more mappings
        }
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/test_handlers.py::test_handle_example_event -v
```

**Example test**:

```python
import pytest
from cloudevents.http import CloudEvent
from app.handlers.order_handler import handle_order_created

@pytest.mark.asyncio
async def test_handle_order_created():
    event = CloudEvent({
        "type": "com.example.order.created",
        "source": "https://example.com/orders",
    }, {
        "orderId": "12345",
        "amount": 99.99
    })
    
    # Should not raise
    await handle_order_created(event)
```

## Structured Logging

All logs output as JSON lines for easy ingestion:

```json
{"event": "Processing order", "timestamp": "2025-01-01T12:00:00Z", "level": "info", "service": "order-processor", "order_id": "12345"}
{"event": "Order processed", "timestamp": "2025-01-01T12:00:01Z", "level": "info", "service": "order-processor", "order_id": "12345"}
```

**Usage in handlers**:

```python
import structlog

logger = structlog.get_logger()

async def handle_event(event: CloudEvent):
    logger.info("Event received", event_type=event["type"])
    logger.error("Processing failed", error="timeout", retry_count=2)
```

## Publishing Messages

To send signed CloudEvents to the queue:

```python
from app.core.cloudevents import CloudEventHandler
from app.core.rabbitmq import publish_message

# Initialize handler with keys
ce_handler = CloudEventHandler(
    signing_key_pem=signing_key,
    verification_key_pem=verification_key,
)

# Create and sign event
event = ce_handler.create_event(
    event_type="com.example.order.created",
    source="https://example.com/orders",
    data={"orderId": "12345", "amount": 99.99},
)

jws_token = ce_handler.sign_event(event)

# Publish to queue
await publish_message(
    url="amqp://guest:guest@localhost:5672/",
    queue_name="orders_queue",
    message_body=jws_token.encode(),
    content_type="application/jose",
)
```

## Deployment

### Docker Build

```bash
# Build image
docker build -t order-processor:latest .

# Run container
docker run -d \
  --env-file .env \
  --name order-processor \
  order-processor:latest
```

### Kubernetes Deployment

```bash
# Create secrets
kubectl create secret generic order-processor-secrets \
  --from-literal=rabbitmq-url='amqp://user:pass@rabbitmq:5672/' \
  --from-file=signing-key=cloudevents_key \
  --from-file=verification-key=cloudevents_key_public.pem

# Deploy
kubectl apply -f deploy/k8s/deployment.yaml

# Check status
kubectl get pods -l app=order-processor
kubectl logs -l app=order-processor -f
```

**Deployment features**:
- 2 replicas for high availability
- Resource requests and limits
- Non-root security context
- Read-only root filesystem
- Secrets from K8s secrets

## Monitoring and Operations

### Key Metrics

Monitor:
- **Message processing rate**: Messages/second
- **Error rate**: Failed messages / total
- **DLQ depth**: Messages in dead letter queue
- **Queue depth**: Backlog size
- **Processing latency**: Time from receive to ACK

### RabbitMQ Management

Access management UI at `http://localhost:15672`:
- View queue depths
- Monitor consumer connections
- Inspect messages in queues
- Purge or move messages
- View DLQ contents

### Inspecting Failed Messages

1. Access RabbitMQ management UI
2. Navigate to Queues
3. Find `{queue_name}.dlq`
4. Use "Get messages" to inspect
5. Fix issue and republish to main queue

### Graceful Shutdown

The worker handles `SIGTERM` and `SIGINT`:
1. Stop accepting new messages
2. Finish processing current messages
3. Close RabbitMQ connection
4. Exit cleanly

Kubernetes sends SIGTERM before SIGKILL (30s grace period by default).

## Common Patterns

### Database Integration

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(settings.DATABASE_URL)

async def get_db() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

# app/handlers/order_handler.py
from app.core.database import get_db

async def handle_order_created(event: CloudEvent):
    data = event.get_data()
    
    async for db in get_db():
        # Use db session
        await db.execute(...)
        await db.commit()
```

### External API Calls

```python
import httpx

async def handle_order_created(event: CloudEvent):
    data = event.get_data()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/orders",
            json=data,
            timeout=30.0,
        )
        response.raise_for_status()
```

### Publishing New Events

```python
from app.core.cloudevents import CloudEventHandler
from app.core.rabbitmq import publish_message
from app.core.config import settings

async def handle_order_created(event: CloudEvent):
    # Process order...
    
    # Publish order confirmation event
    ce_handler = CloudEventHandler(
        signing_key_pem=settings.CLOUDEVENTS_SIGNING_KEY,
        verification_key_pem=settings.CLOUDEVENTS_VERIFICATION_KEY,
    )
    
    confirmation = ce_handler.create_event(
        event_type="com.example.order.confirmed",
        source="https://example.com/workers/order-processor",
        data={"orderId": "12345", "status": "confirmed"},
    )
    
    jws_token = ce_handler.sign_event(confirmation)
    
    await publish_message(
        url=str(settings.RABBITMQ_URL),
        queue_name="notifications_queue",
        message_body=jws_token.encode(),
    )
```

## Best Practices

### Idempotency

Ensure handlers are idempotent (safe to run multiple times):

```python
async def handle_order_created(event: CloudEvent):
    order_id = event.get_data()["orderId"]
    
    # Check if already processed
    if await is_processed(order_id):
        logger.info("Order already processed", order_id=order_id)
        return
    
    # Process order
    await process_order(order_id)
    
    # Mark as processed
    await mark_processed(order_id)
```

### Error Context

Include helpful context in error logs:

```python
try:
    await process_order(order_id)
except Exception as e:
    logger.error(
        "Order processing failed",
        order_id=order_id,
        error=str(e),
        event_id=event["id"],
        exc_info=True,
    )
    raise
```

### Timeouts

Set timeouts for external calls:

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(url, json=data)
```

### Configuration

Never hardcode values - use environment variables:

```python
# ❌ Bad
TIMEOUT = 30

# ✅ Good
class Settings(BaseSettings):
    API_TIMEOUT: int = Field(default=30)
```

## Troubleshooting

### Worker not receiving messages

- Check RabbitMQ connection in logs
- Verify queue name matches
- Check queue bindings in RabbitMQ UI
- Ensure messages are being published

### Signature verification failures

- Verify public/private key pair matches
- Check key format (PEM)
- Ensure sender uses matching private key
- Check CloudEvent structure is valid

### Messages going to DLQ

- Check worker logs for errors
- Inspect DLQ messages in RabbitMQ UI
- Verify event handler logic
- Check external API availability

### High memory usage

- Reduce `PREFETCH_COUNT`
- Check for memory leaks in handlers
- Monitor resource limits
- Profile with memory profiler

## Migration from Existing Workers

If converting an existing worker:

1. **Copy handler logic** to `app/handlers/`
2. **Update imports** to use new structure
3. **Add CloudEvent wrapping** to publishers
4. **Configure environment** in `.env`
5. **Test with sample messages**
6. **Deploy with K8s manifests**

## Summary

This scaffold provides:
- ✅ RabbitMQ message consumption
- ✅ CloudEvents with JWS signing (RS256)
- ✅ Automatic signature verification
- ✅ Retry logic with DLQ
- ✅ Structured JSONL logging
- ✅ Graceful shutdown handling
- ✅ Docker containerization
- ✅ Kubernetes manifests
- ✅ Testing infrastructure
- ✅ Type safety with Pydantic

Use the scaffold script for instant setup, then add your business logic to handlers.
