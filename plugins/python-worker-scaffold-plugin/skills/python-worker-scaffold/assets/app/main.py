"""
Worker entry point for {{PROJECT_NAME}}.

Connects to RabbitMQ and processes signed CloudEvent messages.
"""

import asyncio

from app.consumers.message_consumer import MessageConsumer
from app.core.cloudevents import CloudEventHandler
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rabbitmq import RabbitMQConsumer

# Setup structured logging
logger = setup_logging(settings.WORKER_NAME, settings.LOG_LEVEL)


async def main() -> None:
    """Main worker loop."""
    logger.info(
        "Starting worker",
        worker_name=settings.WORKER_NAME,
        queue=settings.QUEUE_NAME,
    )
    
    # Initialize CloudEvent handler
    ce_handler = CloudEventHandler(
        signing_key_pem=settings.CLOUDEVENTS_SIGNING_KEY,
        verification_key_pem=settings.CLOUDEVENTS_VERIFICATION_KEY,
    )
    
    # Initialize message consumer
    message_consumer = MessageConsumer(ce_handler)
    
    # Initialize RabbitMQ consumer
    rabbitmq = RabbitMQConsumer(
        url=str(settings.RABBITMQ_URL),
        queue_name=settings.QUEUE_NAME,
        prefetch_count=settings.PREFETCH_COUNT,
    )
    
    # Setup signal handlers for graceful shutdown
    rabbitmq.setup_signal_handlers()
    
    try:
        # Connect to RabbitMQ
        await rabbitmq.connect()
        
        logger.info("Worker ready, waiting for messages...")
        
        # Start consuming messages
        await rabbitmq.start_consuming(message_consumer.process_message)
        
    except Exception as e:
        logger.error("Worker error", error=str(e), exc_info=True)
        raise
    
    finally:
        await rabbitmq.stop()
        logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
