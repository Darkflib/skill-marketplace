"""
API routes for {{PROJECT_NAME}}
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["api"])


class MessageResponse(BaseModel):
    """Standard message response."""
    message: str


class Item(BaseModel):
    """Example item model."""
    id: int
    name: str
    description: str | None = None


@router.get("/")
async def root() -> MessageResponse:
    """Root endpoint."""
    return MessageResponse(message="Welcome to {{PROJECT_NAME}} API")


@router.get("/items/{item_id}")
async def get_item(item_id: int) -> Item:
    """Get an item by ID."""
    # Example: This would typically fetch from a database
    if item_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    
    return Item(
        id=item_id,
        name=f"Item {item_id}",
        description="This is an example item",
    )


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    """Create a new item."""
    # Example: This would typically save to a database
    return item
