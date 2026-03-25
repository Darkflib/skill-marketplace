# {{PROJECT_NAME}}

{{DESCRIPTION}}

Background worker for processing signed CloudEvents from RabbitMQ.

## Tech Stack

- **Python 3.12** with UV for package management
- **RabbitMQ** for message queue
- **CloudEvents** with JWS signing (RS256)
- **aio-pika** for async RabbitMQ client
- **structlog** for structured JSONL logging
- **Pydantic** for configuration management

## Project Structure

```
{{PROJECT_NAME}}/
├── app/
│   ├── main.py                 # Worker entry point
│   ├── consumers/              # Message consumers
│   │   ├── __init__.py
│   │   └── message_consumer.py
│   ├── handlers/               # Event handlers (business logic)
│   │   ├── __init__.py
│   │   └── example_handler.py
│   └── core/                   # Core functionality
│       ├── __init__.py
│       ├── config.py           # Configuration
│       ├── logging.py          # Structured logging
│       ├── cloudevents.py      # CloudEvent signing/verification
│       └── rabbitmq.py         # RabbitMQ connection management
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_handlers.py
├── deploy/k8s/                 # Kubernetes manifests
├── pyproject.toml              # Project dependencies
├── Dockerfile                  # Container image
├── docker-compose.yml          # Local development
└── .env.example                # Environment template
```

## Quick Start

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose (recommended)

### Generate CloudEvents Keys

```bash
# Generate RSA key pair for CloudEvents signing
ssh-keygen -t rsa -b 2048 -m PEM -f cloudevents_key
# This creates:
# - cloudevents_key (private key)
# - cloudevents_key.pub (public key - convert to PEM)

# Convert public key to PEM format
ssh-keygen -f cloudevents_key.pub -e -m PEM > cloudevents_key_public.pem
```

### Local Development (with Docker)

1. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your CloudEvents keys
   nano .env
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f worker
   ```

4. **Stop services**:
   ```bash
   docker-compose down
   ```

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start RabbitMQ** (using Docker):
   ```bash
   docker run -d --name rabbitmq \
     -p 5672:5672 \
     -p 15672:15672 \
     rabbitmq:3.13-management-alpine
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Update RABBITMQ_URL to point to localhost
   # Add your CloudEvents keys
   nano .env
   ```

4. **Run worker**:
   ```bash
   uv run python -m app.main
   ```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/test_handlers.py -v
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

### Adding New Event Handlers

1. **Create handler** in `app/handlers/`:
   ```python
   # app/handlers/order_handler.py
   async def handle_order_created(event: CloudEvent) -> None:
       data = event.get_data()
       # Process order...
   ```

2. **Register handler** in `app/consumers/message_consumer.py`:
   ```python
   self.handlers = {
       "com.example.order.created": handle_order_created,
   }
   ```

### Testing Message Processing

```bash
# Send test message using Python
uv run python scripts/send_test_message.py
```

## CloudEvents

### Event Structure

Messages are CloudEvents wrapped in JWS signatures:

```json
{
  "specversion": "1.0",
  "type": "com.example.order.created",
  "source": "https://example.com/orders",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "time": "2025-01-01T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "orderId": "12345",
    "amount": 99.99
  }
}
```

### Signature Verification

The worker automatically:
1. Receives JWS-signed CloudEvent from RabbitMQ
2. Verifies signature using public key
3. Extracts and validates CloudEvent
4. Dispatches to appropriate handler
5. Acknowledges or rejects message

## Error Handling

### Retry Logic

- Failed messages are retried up to `MAX_RETRIES` times
- Retry delay configured by `RETRY_DELAY`
- After max retries, messages move to dead letter queue (DLQ)

### Dead Letter Queue

Failed messages go to: `{QUEUE_NAME}.dlq`

Inspect failed messages:
```bash
# Access RabbitMQ management UI
http://localhost:15672
# Username: guest, Password: guest

# View DLQ messages
# Navigate to Queues > {QUEUE_NAME}.dlq
```

## Deployment

### Build Container Image

```bash
docker build -t {{PROJECT_NAME}}:latest .
```

### Kubernetes Deployment

```bash
# Create secrets
kubectl create secret generic {{PROJECT_NAME}}-secrets \
  --from-literal=rabbitmq-url='amqp://...' \
  --from-file=signing-key=cloudevents_key \
  --from-file=verification-key=cloudevents_key_public.pem

# Apply manifests
kubectl apply -f deploy/k8s/

# Check status
kubectl get deployments
kubectl logs -l app={{PROJECT_NAME}}
```

## Monitoring

### Structured Logs

All logs output as JSON lines for easy aggregation:

```json
{"event": "Message processed successfully", "timestamp": "2025-01-01T12:00:00Z", "level": "info", "service": "{{PROJECT_NAME}}", "message_id": "abc-123"}
```

### Health Metrics

Monitor:
- Message processing rate
- Error rate
- DLQ depth
- Queue depth
- Connection status

## Environment Variables

See `.env.example` for all configuration options.

Required:
- `RABBITMQ_URL`: RabbitMQ connection string
- `CLOUDEVENTS_SIGNING_KEY`: Private key (PEM)
- `CLOUDEVENTS_VERIFICATION_KEY`: Public key (PEM)

## Security

- Non-root container user
- CloudEvents signed with RS256
- Message signatures verified before processing
- Secrets managed via environment variables
- Private keys never committed to git

## License

[Your License Here]
