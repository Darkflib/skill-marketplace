"""
Example event handler.

Business logic for processing specific event types.
"""

import structlog
from cloudevents.http import CloudEvent

logger = structlog.get_logger()


async def handle_example_event(event: CloudEvent) -> None:
    """
    Handle example event.
    
    Args:
        event: CloudEvent to process
    """
    event_data = event.get_data()
    
    logger.info(
        "Processing example event",
        event_id=event["id"],
        event_type=event["type"],
        data=event_data,
    )
    
    # TODO: Implement your business logic here
    # Examples:
    # - Update database
    # - Call external API
    # - Send notifications
    # - Transform and publish new events
    
    # Simulate processing
    logger.info("Example event processed successfully", event_id=event["id"])
