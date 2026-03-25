"""
Example message consumer for CloudEvents.

Consumes messages from RabbitMQ, verifies CloudEvent signatures,
and dispatches to appropriate handlers.
"""

import structlog
from aio_pika import IncomingMessage
from cloudevents.http import CloudEvent

from app.core.cloudevents import CloudEventHandler
from app.core.config import settings
from app.handlers.example_handler import handle_example_event

logger = structlog.get_logger()


class MessageConsumer:
    """Consumer for signed CloudEvent messages."""
    
    def __init__(self, ce_handler: CloudEventHandler):
        """
        Initialize consumer.
        
        Args:
            ce_handler: CloudEvent handler for verification
        """
        self.ce_handler = ce_handler
        
        # Map event types to handlers
        self.handlers = {
            "com.example.event.created": handle_example_event,
            # Add more event type -> handler mappings here
        }
    
    async def process_message(self, message: IncomingMessage) -> None:
        """
        Process incoming RabbitMQ message.
        
        Args:
            message: Incoming message from RabbitMQ
        """
        async with message.process(ignore_processed=True):
            try:
                # Decode message body
                jws_token = message.body.decode("utf-8")
                
                logger.info(
                    "Received message",
                    message_id=message.message_id,
                    routing_key=message.routing_key,
                )
                
                # Verify signature and extract CloudEvent
                event = self.ce_handler.verify_and_extract(jws_token)
                
                logger.info(
                    "CloudEvent verified",
                    event_type=event["type"],
                    event_id=event["id"],
                    source=event["source"],
                )
                
                # Dispatch to handler
                await self.dispatch_event(event)
                
                # Acknowledge message
                await message.ack()
                
                logger.info("Message processed successfully", message_id=message.message_id)
                
            except ValueError as e:
                # Verification failed - reject and send to DLQ
                logger.error(
                    "CloudEvent verification failed",
                    error=str(e),
                    message_id=message.message_id,
                )
                await message.reject(requeue=False)
                
            except Exception as e:
                # Processing error - reject with retry
                logger.error(
                    "Message processing failed",
                    error=str(e),
                    message_id=message.message_id,
                    exc_info=True,
                )
                
                # Check retry count
                retry_count = message.headers.get("x-retry-count", 0) if message.headers else 0
                
                if retry_count < settings.MAX_RETRIES:
                    # Requeue for retry
                    await message.reject(requeue=True)
                    logger.info("Message requeued for retry", retry_count=retry_count + 1)
                else:
                    # Max retries exceeded - send to DLQ
                    await message.reject(requeue=False)
                    logger.error("Max retries exceeded, sent to DLQ")
    
    async def dispatch_event(self, event: CloudEvent) -> None:
        """
        Dispatch CloudEvent to appropriate handler.
        
        Args:
            event: Verified CloudEvent
            
        Raises:
            ValueError: If no handler found for event type
        """
        event_type = event["type"]
        
        handler = self.handlers.get(event_type)
        
        if not handler:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        await handler(event)
