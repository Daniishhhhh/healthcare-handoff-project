"""Handoff service for managing patient handoff workflows."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid

from app.models.handoff import Handoff, HandoffStatusEnum, HandoffPriorityEnum
from app.models.handoff_item import HandoffItem, ItemStatusEnum, ItemTypeEnum
from app.repositories.handoff_repo import HandoffRepository
from app.repositories.item_repo import HandoffItemRepository
from app.repositories.patient_repo import PatientRepository
from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService
from app.exceptions import (
    ResourceNotFound,
    InvalidStateTransition,
    Forbidden,
)


class HandoffService:
    """Service for managing handoff workflows."""

    # Valid state transitions
    STATE_TRANSITIONS = {
        HandoffStatusEnum.DRAFT: [HandoffStatusEnum.PENDING_REVIEW, HandoffStatusEnum.ESCALATED],
        HandoffStatusEnum.PENDING_REVIEW: [HandoffStatusEnum.ACCEPTED, HandoffStatusEnum.ESCALATED],
        HandoffStatusEnum.ACCEPTED: [HandoffStatusEnum.COMPLETED, HandoffStatusEnum.ESCALATED],
        HandoffStatusEnum.COMPLETED: [],
        HandoffStatusEnum.ESCALATED: [HandoffStatusEnum.PENDING_REVIEW, HandoffStatusEnum.ACCEPTED],
    }

    def __init__(self, db: Session):
        self.db = db
        self.handoff_repo = HandoffRepository(db)
        self.item_repo = HandoffItemRepository(db)
        self.patient_repo = PatientRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    def create_handoff(
        self,
        patient_id: str,
        created_by: str,
        assigned_to: str,
        priority: str,
        diagnosis_summary: str,
        pending_tests: Optional[str] = None,
        medication_changes: Optional[str] = None,
        follow_up_deadline: Optional[datetime] = None,
        additional_notes: Optional[str] = None,
    ) -> Handoff:
        """Create a new handoff in DRAFT status."""
        
        # Validate patient exists
        patient = self.patient_repo.get(patient_id)
        if not patient:
            raise ResourceNotFound("Patient", patient_id)
        
        # Validate assigned_to user exists
        assigned_user = self.user_repo.get(assigned_to)
        if not assigned_user:
            raise ResourceNotFound("User", assigned_to)
        
        # Validate creator exists
        creator = self.user_repo.get(created_by)
        if not creator:
            raise ResourceNotFound("User", created_by)

        handoff = Handoff(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            created_by=created_by,
            assigned_to=assigned_to,
            status=HandoffStatusEnum.DRAFT,
            priority=HandoffPriorityEnum(priority),
            diagnosis_summary=diagnosis_summary,
            pending_tests=pending_tests,
            medication_changes=medication_changes,
            follow_up_deadline=follow_up_deadline,
            additional_notes=additional_notes,
            is_ready=False,
        )

        handoff = self.handoff_repo.create(handoff)

        self.audit_service.log_action(
            user_id=created_by,
            entity_type="HANDOFF",
            entity_id=handoff.id,
            action="CREATE",
            new_values=handoff.to_dict(),
            reason=f"Created handoff for patient {patient_id}",
        )

        return handoff

    def update_handoff(
        self,
        handoff_id: str,
        user_id: str,
        **kwargs,
    ) -> Handoff:
        """Update handoff (only allowed in DRAFT status)."""
        
        handoff = self.handoff_repo.get(handoff_id)
        if not handoff:
            raise ResourceNotFound("Handoff", handoff_id)
        
        # Only creator or admin can update
        if handoff.created_by != user_id:
            raise Forbidden("Only creator can update handoff")
        
        # Only allow updates in DRAFT status
        if handoff.status != HandoffStatusEnum.DRAFT:
            raise InvalidStateTransition(handoff.status.value, "UPDATE")

        old_values = handoff.to_dict()
        
        # Update allowed fields
        allowed_fields = {
            "diagnosis_summary", "pending_tests", "medication_changes",
            "follow_up_deadline", "additional_notes", "priority", "assigned_to"
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(handoff, field, value)
        
        handoff.updated_at = datetime.utcnow()
        handoff = self.handoff_repo.create(handoff)

        self.audit_service.log_action(
            user_id=user_id,
            entity_type="HANDOFF",
            entity_id=handoff.id,
            action="UPDATE",
            old_values=old_values,
            new_values=handoff.to_dict(),
            reason="Updated handoff details",
        )

        return handoff

    def transition_status(
        self,
        handoff_id: str,
        new_status: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> Handoff:
        """Transition handoff to new status (validate state machine)."""
        
        handoff = self.handoff_repo.get(handoff_id)
        if not handoff:
            raise ResourceNotFound("Handoff", handoff_id)
        
        # Convert string to enum if needed
        if isinstance(new_status, str):
            try:
                new_status_enum = HandoffStatusEnum[new_status.upper()]
            except KeyError:
                raise InvalidStateTransition(handoff.status.value, new_status)
        else:
            new_status_enum = new_status

        # Validate transition is allowed
        if new_status_enum not in self.STATE_TRANSITIONS.get(handoff.status, []):
            raise InvalidStateTransition(handoff.status.value, new_status_enum.value)

        old_status = handoff.status.value
        handoff.status = new_status_enum

        # Set timestamp for accepted/completed
        if new_status_enum == HandoffStatusEnum.ACCEPTED:
            handoff.accepted_at = datetime.utcnow()
        elif new_status_enum == HandoffStatusEnum.COMPLETED:
            handoff.completed_at = datetime.utcnow()

        handoff.updated_at = datetime.utcnow()
        handoff = self.handoff_repo.create(handoff)

        self.audit_service.log_action(
            user_id=user_id,
            entity_type="HANDOFF",
            entity_id=handoff.id,
            action="UPDATE",
            old_values={"status": old_status},
            new_values={"status": new_status_enum.value},
            reason=reason or f"Transitioned from {old_status} to {new_status_enum.value}",
        )

        return handoff

    def add_item(
        self,
        handoff_id: str,
        title: str,
        item_type: str,
        assigned_to: str,
        user_id: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> HandoffItem:
        """Add a task item to a handoff."""
        
        handoff = self.handoff_repo.get(handoff_id)
        if not handoff:
            raise ResourceNotFound("Handoff", handoff_id)
        
        # Validate assigned_to user exists
        assigned_user = self.user_repo.get(assigned_to)
        if not assigned_user:
            raise ResourceNotFound("User", assigned_to)

        item = HandoffItem(
            id=str(uuid.uuid4()),
            handoff_id=handoff_id,
            title=title,
            description=description,
            item_type=ItemTypeEnum(item_type),
            assigned_to=assigned_to,
            due_date=due_date,
            status=ItemStatusEnum.OPEN,
        )

        item = self.item_repo.create(item)

        self.audit_service.log_action(
            user_id=user_id,
            entity_type="HANDOFF_ITEM",
            entity_id=item.id,
            action="CREATE",
            new_values=item.to_dict(),
            reason=f"Added task item to handoff {handoff_id}",
        )

        return item

    def update_item_status(
        self,
        item_id: str,
        new_status: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> HandoffItem:
        """Update item status (OPEN -> IN_PROGRESS -> COMPLETED)."""
        
        item = self.item_repo.get(item_id)
        if not item:
            raise ResourceNotFound("HandoffItem", item_id)
        
        # Validate new status
        try:
            status_enum = ItemStatusEnum[new_status.upper()]
        except KeyError:
            raise InvalidStateTransition(item.status.value, new_status)

        old_status = item.status.value
        item.status = status_enum

        if status_enum == ItemStatusEnum.COMPLETED:
            item.completed_at = datetime.utcnow()

        item.updated_at = datetime.utcnow()
        item = self.item_repo.create(item)

        self.audit_service.log_action(
            user_id=user_id,
            entity_type="HANDOFF_ITEM",
            entity_id=item.id,
            action="UPDATE",
            old_values={"status": old_status},
            new_values={"status": status_enum.value},
            reason=reason or f"Updated status from {old_status} to {status_enum.value}",
        )

        return item

    def get_handoff_with_items(self, handoff_id: str) -> dict:
        """Get handoff with all associated items."""
        
        handoff = self.handoff_repo.get(handoff_id)
        if not handoff:
            raise ResourceNotFound("Handoff", handoff_id)
        
        items = self.item_repo.find_by_handoff(handoff_id)

        return {
            "handoff": handoff,
            "items": items,
        }

    def get_user_handoffs(self, user_id: str, role: str) -> List[Handoff]:
        """Get handoffs relevant to user based on role."""
        
        if role == "admin":
            # Admins see all active handoffs
            return self.handoff_repo.find_active_handoffs()
        else:
            # Others see only assigned to them or created by them
            assigned = self.handoff_repo.find_by_assigned_to(user_id)
            created = self.handoff_repo.find_by_created_by(user_id)
            
            # Combine and deduplicate by ID
            all_handoffs = {h.id: h for h in assigned + created}
            return list(all_handoffs.values())