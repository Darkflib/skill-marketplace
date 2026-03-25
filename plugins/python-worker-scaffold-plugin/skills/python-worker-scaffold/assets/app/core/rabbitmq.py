"""
RabbitMQ connection and consumer management.

Provides robust connection handling with automatic reconnection,
graceful shutdown, and consumer registration.
"""

import asyncio
import signal
from typing import Callable

import aio_pika
import structlog
from aio_pika import ExchangeType, IncomingMessage
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

logger = structlog.get_logger()


class RabbitMQConsumer:
    """RabbitMQ consumer with automatic reconnection."""
    
    def __init__(
        self,
        url: str,
        queue_name: str,
        prefetch_count: int = 10,
    ):
        """
        Initialize RabbitMQ consumer.
        
        Args:
            url: RabbitMQ connection URL
            queue_name: Queue name to consume from
            prefetch_count: Number of messages to prefetch
        """
        self.url = url
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count
        
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.queue: AbstractQueue | None = None
        self.should_stop = False
    
    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        logger.info("Connecting to RabbitMQ", url=self.url)
        
        self.connection = await aio_pika.connect_robust(
            self.url,
            timeout=30,
        )
        
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)
        
        # Declare queue (idempotent)
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                # Dead letter exchange for failed messages
                "x-dead-letter-exchange": f"{self.queue_name}.dlx",
            },
        )
        
        # Declare dead letter exchange and queue
        dlx = await self.channel.declare_exchange(
            f"{self.queue_name}.dlx",
            ExchangeType.DIRECT,
            durable=True,
        )
        
        dlq = await self.channel.declare_queue(
            f"{self.queue_name}.dlq",
            durable=True,
        )
        
        await dlq.bind(dlx)
        
        logger.info(
            "Connected to RabbitMQ",
            queue=self.queue_name,
            prefetch_count=self.prefetch_count,
        )
    
    async def start_consuming(
        self,
        message_handler: Callable[[IncomingMessage], None],
    ) -> None:
        """
        Start consuming messages.
        
        Args:
            message_handler: Async function to handle incoming messages
        """
        if not self.queue:
            raise RuntimeError("Not connected to RabbitMQ")
        
        logger.info("Starting message consumer", queue=self.queue_name)
        
        await self.queue.consume(message_handler)
        
        # Keep running until stopped
        while not self.should_stop:
            await asyncio.sleep(1)
    
    async def stop(self) -> None:
        """Stop consuming and close connections gracefully."""
        logger.info("Stopping RabbitMQ consumer")
        self.should_stop = True
        
        if self.channel:
            await self.channel.close()
        
        if self.connection:
            await self.connection.close()
        
        logger.info("RabbitMQ consumer stopped")
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.stop()),
            )
        
        logger.info("Signal handlers registered")


async def publish_message(
    url: str,
    queue_name: str,
    message_body: bytes,
    content_type: str = "application/json",
) -> None:
    """
    Publish a single message to a queue.
    
    Args:
        url: RabbitMQ connection URL
        queue_name: Queue name to publish to
        message_body: Message body as bytes
        content_type: Content type header
    """
    connection = await aio_pika.connect_robust(url)
    
    try:
        channel = await connection.channel()
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                content_type=content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )
        
        logger.info("Message published", queue=queue_name)
        
    finally:
        await connection.close()
