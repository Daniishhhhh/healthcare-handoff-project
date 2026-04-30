"""Handoff API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.handoff import HandoffStatusEnum
import uuid

from app.db.database import get_db
from app.dependencies import get_current_user, require_role, CurrentUser
from app.schemas.handoff import HandoffCreate, HandoffResponse
from app.services.handoff_service import HandoffService
from app.services.readiness_service import ReadinessService
from app.services.escalation_service import EscalationService
from app.exceptions import ResourceNotFound, Forbidden
from datetime import datetime

router = APIRouter(prefix="/handoffs", tags=["handoffs"])


@router.post("", response_model=HandoffResponse, status_code=status.HTTP_201_CREATED)
async def create_handoff(
    request: HandoffCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("doctor", "admin")),
):
    """Create a new handoff (doctor/admin only)."""
    
    service = HandoffService(db)
    
    handoff = service.create_handoff(
        patient_id=request.patient_id,
        created_by=current_user.user_id,
        assigned_to=request.assigned_to,
        priority=request.priority.value,
        diagnosis_summary=request.diagnosis_summary,
        pending_tests=request.pending_tests,
        medication_changes=request.medication_changes,
        follow_up_deadline=request.follow_up_deadline,
        additional_notes=request.additional_notes,
    )
    
    return HandoffResponse(
        id=handoff.id,
        patient_id=handoff.patient_id,
        created_by=handoff.created_by,
        assigned_to=handoff.assigned_to,
        status=handoff.status.value,
        priority=handoff.priority.value,
        is_ready=handoff.is_ready,
        diagnosis_summary=handoff.diagnosis_summary,
        pending_tests=handoff.pending_tests,
        medication_changes=handoff.medication_changes,
        follow_up_deadline=handoff.follow_up_deadline.isoformat() if handoff.follow_up_deadline else None,
        additional_notes=handoff.additional_notes,
        created_at=handoff.created_at.isoformat(),
        updated_at=handoff.updated_at.isoformat(),
        accepted_at=handoff.accepted_at.isoformat() if handoff.accepted_at else None,
        completed_at=handoff.completed_at.isoformat() if handoff.completed_at else None,
    )


@router.get("/{handoff_id}", response_model=HandoffResponse)
async def get_handoff(
    handoff_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get handoff by ID."""
    
    service = HandoffService(db)
    data = service.get_handoff_with_items(handoff_id)
    handoff = data["handoff"]
    
    # Check authorization (creator, assigned_to, or admin)
    if not (current_user.user_id in [handoff.created_by, handoff.assigned_to] or current_user.is_admin()):
        raise Forbidden("Not authorized to view this handoff")
    
    return HandoffResponse(
        id=handoff.id,
        patient_id=handoff.patient_id,
        created_by=handoff.created_by,
        assigned_to=handoff.assigned_to,
        status=handoff.status.value,
        priority=handoff.priority.value,
        is_ready=handoff.is_ready,
        diagnosis_summary=handoff.diagnosis_summary,
        pending_tests=handoff.pending_tests,
        medication_changes=handoff.medication_changes,
        follow_up_deadline=handoff.follow_up_deadline.isoformat() if handoff.follow_up_deadline else None,
        additional_notes=handoff.additional_notes,
        created_at=handoff.created_at.isoformat(),
        updated_at=handoff.updated_at.isoformat(),
        accepted_at=handoff.accepted_at.isoformat() if handoff.accepted_at else None,
        completed_at=handoff.completed_at.isoformat() if handoff.completed_at else None,
    )


@router.patch("/{handoff_id}", response_model=HandoffResponse)
async def update_handoff(
    handoff_id: str,
    request: HandoffCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update handoff (only in DRAFT status)."""
    
    service = HandoffService(db)
    
    handoff = service.update_handoff(
        handoff_id=handoff_id,
        user_id=current_user.user_id,
        diagnosis_summary=request.diagnosis_summary,
        pending_tests=request.pending_tests,
        medication_changes=request.medication_changes,
        follow_up_deadline=request.follow_up_deadline,
        additional_notes=request.additional_notes,
        priority=request.priority.value,
        assigned_to=request.assigned_to,
    )
    
    return HandoffResponse(
        id=handoff.id,
        patient_id=handoff.patient_id,
        created_by=handoff.created_by,
        assigned_to=handoff.assigned_to,
        status=handoff.status.value,
        priority=handoff.priority.value,
        is_ready=handoff.is_ready,
        diagnosis_summary=handoff.diagnosis_summary,
        pending_tests=handoff.pending_tests,
        medication_changes=handoff.medication_changes,
        follow_up_deadline=handoff.follow_up_deadline.isoformat() if handoff.follow_up_deadline else None,
        additional_notes=handoff.additional_notes,
        created_at=handoff.created_at.isoformat(),
        updated_at=handoff.updated_at.isoformat(),
        accepted_at=handoff.accepted_at.isoformat() if handoff.accepted_at else None,
        completed_at=handoff.completed_at.isoformat() if handoff.completed_at else None,
    )


@router.post("/{handoff_id}/readiness-check", status_code=status.HTTP_200_OK)
async def check_readiness(
    handoff_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Check if handoff is ready for acceptance."""
    
    service = HandoffService(db)
    readiness_service = ReadinessService(db)
    
    handoff = service.handoff_repo.get(handoff_id)
    if not handoff:
        raise ResourceNotFound("Handoff", handoff_id)
    
    # Check authorization
    if not (current_user.user_id in [handoff.created_by, handoff.assigned_to] or current_user.is_admin()):
        raise Forbidden("Not authorized to check this handoff")
    
    return readiness_service.get_readiness_summary(handoff)


@router.post("/{handoff_id}/accept", response_model=HandoffResponse, status_code=status.HTTP_200_OK)
async def accept_handoff(
    handoff_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Accept handoff (must pass readiness check)."""
    
    service = HandoffService(db)
    readiness_service = ReadinessService(db)
    
    handoff = service.handoff_repo.get(handoff_id)
    if not handoff:
        raise ResourceNotFound("Handoff", handoff_id)
    
    if current_user.user_id != handoff.assigned_to and not current_user.is_admin():
        raise Forbidden("Only assigned user can accept handoff")
    
    # Validate readiness
    readiness_service.assert_ready(handoff)
    
    # Update readiness check result
    result = readiness_service.validate_handoff(handoff)
    handoff.is_ready = result["is_ready"]
    handoff.last_readiness_check_at = datetime.utcnow()
    handoff.readiness_check_result = result
    
    # Transition: DRAFT → PENDING_REVIEW (if needed)
    if handoff.status == HandoffStatusEnum.DRAFT:
        handoff = service.transition_status(
            handoff_id=handoff_id,
            new_status="PENDING_REVIEW",
            user_id=current_user.user_id,
            reason="User submitted for review",
        )
    
    # Transition: PENDING_REVIEW → ACCEPTED
    handoff = service.transition_status(
        handoff_id=handoff_id,
        new_status="ACCEPTED",
        user_id=current_user.user_id,
        reason="User accepted handoff after readiness check",
    )
    
    return HandoffResponse(
        id=handoff.id,
        patient_id=handoff.patient_id,
        created_by=handoff.created_by,
        assigned_to=handoff.assigned_to,
        status=handoff.status.value,
        priority=handoff.priority.value,
        is_ready=handoff.is_ready,
        diagnosis_summary=handoff.diagnosis_summary,
        pending_tests=handoff.pending_tests,
        medication_changes=handoff.medication_changes,
        follow_up_deadline=handoff.follow_up_deadline.isoformat() if handoff.follow_up_deadline else None,
        additional_notes=handoff.additional_notes,
        created_at=handoff.created_at.isoformat(),
        updated_at=handoff.updated_at.isoformat(),
        accepted_at=handoff.accepted_at.isoformat() if handoff.accepted_at else None,
        completed_at=handoff.completed_at.isoformat() if handoff.completed_at else None,
    )


@router.post("/{handoff_id}/escalate", status_code=status.HTTP_200_OK)
async def escalate_handoff(
    handoff_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Manually escalate a handoff."""
    
    service = EscalationService(db)
    handoff_service = HandoffService(db)
    
    event = service.escalate_handoff(
        handoff_id=handoff_id,
        triggered_by="MANUAL",
        reason=reason,
        user_id=current_user.user_id,
        action_taken=f"Escalated by {current_user.email}",
    )
    
    handoff = handoff_service.handoff_repo.get(handoff_id)
    
    return {
        "escalation_event": {
            "id": event.id,
            "handoff_id": event.handoff_id,
            "triggered_by": event.triggered_by,
            "reason": event.reason,
            "action_taken": event.action_taken,
            "created_at": event.created_at.isoformat(),
        },
        "handoff_status": handoff.status.value,
    }


@router.post("/{handoff_id}/complete", response_model=HandoffResponse)
async def complete_handoff(
    handoff_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Mark handoff as completed."""
    
    service = HandoffService(db)
    
    handoff = service.handoff_repo.get(handoff_id)
    if not handoff:
        raise ResourceNotFound("Handoff", handoff_id)
    
    # Only assigned_to or creator can complete
    if current_user.user_id not in [handoff.assigned_to, handoff.created_by] and not current_user.is_admin():
        raise Forbidden("Not authorized to complete this handoff")
    
    handoff = service.transition_status(
        handoff_id=handoff_id,
        new_status="COMPLETED",
        user_id=current_user.user_id,
        reason="Handoff completed",
    )
    
    return HandoffResponse(
        id=handoff.id,
        patient_id=handoff.patient_id,
        created_by=handoff.created_by,
        assigned_to=handoff.assigned_to,
        status=handoff.status.value,
        priority=handoff.priority.value,
        is_ready=handoff.is_ready,
        diagnosis_summary=handoff.diagnosis_summary,
        pending_tests=handoff.pending_tests,
        medication_changes=handoff.medication_changes,
        follow_up_deadline=handoff.follow_up_deadline.isoformat() if handoff.follow_up_deadline else None,
        additional_notes=handoff.additional_notes,
        created_at=handoff.created_at.isoformat(),
        updated_at=handoff.updated_at.isoformat(),
        accepted_at=handoff.accepted_at.isoformat() if handoff.accepted_at else None,
        completed_at=handoff.completed_at.isoformat() if handoff.completed_at else None,
    )