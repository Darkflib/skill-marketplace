"""
Tests for event handlers.
"""

import pytest
from cloudevents.http import CloudEvent

from app.handlers.example_handler import handle_example_event


@pytest.mark.asyncio
async def test_handle_example_event():
    """Test example event handler."""
    # Create test CloudEvent
    event = CloudEvent({
        "type": "com.example.event.created",
        "source": "https://example.com/test",
    }, {
        "test_key": "test_value"
    })
    
    # Should not raise any exceptions
    await handle_example_event(event)
