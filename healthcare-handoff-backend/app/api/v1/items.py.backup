"""Handoff item API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.item import ItemCreate, ItemResponse
from app.services.handoff_service import HandoffService
from app.exceptions import ResourceNotFound, Forbidden

router = APIRouter(prefix="/handoffs", tags=["items"])


class ItemStatusUpdate(BaseModel):
    """Request to update item status."""
    status: str = Field(..., min_length=1)


@router.post("/{handoff_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    handoff_id: str,
    request: ItemCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Add a task item to a handoff."""
    
    service = HandoffService(db)
    
    item = service.add_item(
        handoff_id=handoff_id,
        title=request.title,
        item_type=request.item_type.value,
        assigned_to=request.assigned_to,
        user_id=current_user.user_id,
        description=request.description,
        due_date=request.due_date,
    )
    
    return ItemResponse(
        id=item.id,
        handoff_id=item.handoff_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type.value,
        assigned_to=item.assigned_to,
        due_date=item.due_date.isoformat() if item.due_date else None,
        status=item.status.value,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
        completed_at=item.completed_at.isoformat() if item.completed_at else None,
    )


@router.get("/{handoff_id}/items")
async def list_items(
    handoff_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all items in a handoff."""
    
    service = HandoffService(db)
    data = service.get_handoff_with_items(handoff_id)
    
    handoff = data["handoff"]
    items = data["items"]
    
    # Check authorization
    if not (current_user.user_id in [handoff.created_by, handoff.assigned_to] or current_user.is_admin()):
        raise Forbidden("Not authorized to view this handoff")
    
    return {
        "handoff_id": handoff_id,
        "item_count": len(items),
        "items": [
            ItemResponse(
                id=item.id,
                handoff_id=item.handoff_id,
                title=item.title,
                description=item.description,
                item_type=item.item_type.value,
                assigned_to=item.assigned_to,
                due_date=item.due_date.isoformat() if item.due_date else None,
                status=item.status.value,
                created_at=item.created_at.isoformat(),
                updated_at=item.updated_at.isoformat(),
                completed_at=item.completed_at.isoformat() if item.completed_at else None,
            )
            for item in items
        ],
    }


@router.patch("/{handoff_id}/items/{item_id}", response_model=ItemResponse)
async def update_item_status(
    handoff_id: str,
    item_id: str,
    request: ItemStatusUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update item status (OPEN -> IN_PROGRESS -> COMPLETED)."""
    
    service = HandoffService(db)
    
    # Verify item exists and belongs to handoff
    item = service.item_repo.get(item_id)
    if not item or item.handoff_id != handoff_id:
        raise ResourceNotFound("HandoffItem", item_id)
    
    # Update item status
    item = service.update_item_status(
        item_id=item_id,
        new_status=request.status,
        user_id=current_user.user_id,
        reason=f"Status updated to {request.status}",
    )
    
    return ItemResponse(
        id=item.id,
        handoff_id=item.handoff_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type.value,
        assigned_to=item.assigned_to,
        due_date=item.due_date.isoformat() if item.due_date else None,
        status=item.status.value,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
        completed_at=item.completed_at.isoformat() if item.completed_at else None,
    )


@router.get("/{handoff_id}/items/{item_id}", response_model=ItemResponse)
async def get_item(
    handoff_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get a specific item."""
    
    service = HandoffService(db)
    
    item = service.item_repo.get(item_id)
    if not item or item.handoff_id != handoff_id:
        raise ResourceNotFound("HandoffItem", item_id)
    
    # Check authorization via handoff
    handoff = service.handoff_repo.get(handoff_id)
    if not (current_user.user_id in [handoff.created_by, handoff.assigned_to] or current_user.is_admin()):
        raise Forbidden("Not authorized to view this item")
    
    return ItemResponse(
        id=item.id,
        handoff_id=item.handoff_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type.value,
        assigned_to=item.assigned_to,
        due_date=item.due_date.isoformat() if item.due_date else None,
        status=item.status.value,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
        completed_at=item.completed_at.isoformat() if item.completed_at else None,
    )