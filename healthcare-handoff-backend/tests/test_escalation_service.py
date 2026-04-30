"""Unit tests for EscalationService."""

import pytest
import uuid
from datetime import datetime, timedelta

from app.services.escalation_service import EscalationService
from app.models.handoff import Handoff, HandoffStatusEnum, HandoffPriorityEnum
from app.models.handoff_item import HandoffItem, ItemTypeEnum, ItemStatusEnum
from app.models.user import User, RoleEnum
from app.models.patient import Patient
from app.utils import hash_password


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def esc_user(db_session):
    user = User(
        id=str(uuid.uuid4()),
        email="esc_doc@example.com",
        hashed_password=hash_password("Password123!"),
        role=RoleEnum.DOCTOR,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def esc_patient(db_session, esc_user):
    patient = Patient(
        id=str(uuid.uuid4()),
        mrn="MRN-ESC-001",
        name="Escalation Patient",
        created_by=esc_user.id,
    )
    db_session.add(patient)
    db_session.commit()
    return patient


@pytest.fixture
def esc_handoff(db_session, esc_user, esc_patient):
    handoff = Handoff(
        id=str(uuid.uuid4()),
        patient_id=esc_patient.id,
        created_by=esc_user.id,
        assigned_to=esc_user.id,
        status=HandoffStatusEnum.DRAFT,
        priority=HandoffPriorityEnum.MEDIUM,
        diagnosis_summary="Patient recovering from surgery.",
        follow_up_deadline=datetime.utcnow() + timedelta(days=7),
        is_ready=False,
    )
    db_session.add(handoff)
    db_session.commit()
    return handoff


# ── escalate_handoff ──────────────────────────────────────────────────────────

def test_escalate_handoff_transitions_to_escalated(db_session, esc_user, esc_handoff):
    """Escalating a DRAFT handoff transitions its status to ESCALATED."""
    service = EscalationService(db_session)
    event = service.escalate_handoff(
        handoff_id=esc_handoff.id,
        triggered_by="MANUAL",
        reason="Patient condition worsened",
        user_id=esc_user.id,
        action_taken="Doctor escalated manually",
    )

    assert event.handoff_id == esc_handoff.id
    assert event.triggered_by == "MANUAL"
    assert event.reason == "Patient condition worsened"

    db_session.refresh(esc_handoff)
    assert esc_handoff.status == HandoffStatusEnum.ESCALATED


def test_escalate_handoff_creates_event(db_session, esc_user, esc_handoff):
    """Escalating a handoff creates a persisted EscalationEvent record."""
    service = EscalationService(db_session)
    event = service.escalate_handoff(
        handoff_id=esc_handoff.id,
        triggered_by="AUTO",
        reason="Overdue items detected",
        user_id=esc_user.id,
    )

    assert event.id is not None
    # Retrieve from DB to confirm persistence
    history = service.get_escalation_history(esc_handoff.id)
    assert len(history) >= 1
    assert any(e.id == event.id for e in history)


def test_escalate_already_escalated_creates_new_event(db_session, esc_user, esc_handoff):
    """Escalating an already-ESCALATED handoff creates a new event without re-transitioning."""
    service = EscalationService(db_session)

    # First escalation
    service.escalate_handoff(
        handoff_id=esc_handoff.id,
        triggered_by="MANUAL",
        reason="First escalation",
        user_id=esc_user.id,
    )
    db_session.refresh(esc_handoff)
    assert esc_handoff.status == HandoffStatusEnum.ESCALATED

    # Second escalation
    event2 = service.escalate_handoff(
        handoff_id=esc_handoff.id,
        triggered_by="MANUAL",
        reason="Second escalation",
        user_id=esc_user.id,
    )

    db_session.refresh(esc_handoff)
    assert esc_handoff.status == HandoffStatusEnum.ESCALATED  # Unchanged
    history = service.get_escalation_history(esc_handoff.id)
    assert len(history) == 2


def test_escalate_nonexistent_handoff_raises(db_session, esc_user):
    """Escalating a non-existent handoff raises ResourceNotFound."""
    from app.exceptions import ResourceNotFound

    service = EscalationService(db_session)
    with pytest.raises(ResourceNotFound):
        service.escalate_handoff(
            handoff_id="nonexistent-id",
            triggered_by="MANUAL",
            reason="Reason",
            user_id=esc_user.id,
        )


# ── resolve_escalation ────────────────────────────────────────────────────────

def test_resolve_escalation_transitions_to_pending_review(db_session, esc_user, esc_handoff):
    """Resolving an escalation transitions the handoff to PENDING_REVIEW."""
    service = EscalationService(db_session)

    service.escalate_handoff(
        handoff_id=esc_handoff.id,
        triggered_by="MANUAL",
        reason="Reason",
        user_id=esc_user.id,
    )

    resolved = service.resolve_escalation(
        handoff_id=esc_handoff.id,
        user_id=esc_user.id,
        action_taken="Issue resolved by attending physician",
    )

    assert resolved.status == HandoffStatusEnum.PENDING_REVIEW
    db_session.refresh(esc_handoff)
    assert esc_handoff.status == HandoffStatusEnum.PENDING_REVIEW


def test_resolve_non_escalated_handoff_raises(db_session, esc_user, esc_handoff):
    """Resolving a handoff that is not in ESCALATED status raises ValueError."""
    service = EscalationService(db_session)
    assert esc_handoff.status == HandoffStatusEnum.DRAFT

    with pytest.raises(ValueError, match="ESCALATED"):
        service.resolve_escalation(
            handoff_id=esc_handoff.id,
            user_id=esc_user.id,
            action_taken="Attempted resolution",
        )


def test_resolve_nonexistent_handoff_raises(db_session, esc_user):
    """Resolving a non-existent handoff raises ResourceNotFound."""
    from app.exceptions import ResourceNotFound

    service = EscalationService(db_session)
    with pytest.raises(ResourceNotFound):
        service.resolve_escalation(
            handoff_id="nonexistent-id",
            user_id=esc_user.id,
            action_taken="Action",
        )


# ── get_escalation_history ────────────────────────────────────────────────────

def test_get_escalation_history_empty(db_session, esc_user, esc_handoff):
    """A fresh handoff has no escalation history."""
    service = EscalationService(db_session)
    history = service.get_escalation_history(esc_handoff.id)
    assert history == []


def test_get_escalation_history_returns_events(db_session, esc_user, esc_handoff):
    """History returns all escalation events for a handoff."""
    service = EscalationService(db_session)

    service.escalate_handoff(esc_handoff.id, "MANUAL", "Reason 1", esc_user.id)
    # Re-escalate after it's already escalated (creates second event)
    service.escalate_handoff(esc_handoff.id, "AUTO", "Reason 2", esc_user.id)

    history = service.get_escalation_history(esc_handoff.id)
    assert len(history) == 2
    reasons = {e.reason for e in history}
    assert "Reason 1" in reasons
    assert "Reason 2" in reasons


# ── check_and_escalate_overdue ────────────────────────────────────────────────

def test_check_and_escalate_overdue_creates_events(db_session, esc_user, esc_patient):
    """Overdue items in active handoffs trigger automatic escalation."""
    # Create an ACCEPTED handoff (find_active_handoffs returns ACCEPTED + PENDING_REVIEW)
    handoff = Handoff(
        id=str(uuid.uuid4()),
        patient_id=esc_patient.id,
        created_by=esc_user.id,
        assigned_to=esc_user.id,
        status=HandoffStatusEnum.ACCEPTED,
        priority=HandoffPriorityEnum.MEDIUM,
        diagnosis_summary="Post-op monitoring.",
        follow_up_deadline=datetime.utcnow() + timedelta(days=2),
        is_ready=True,
    )
    db_session.add(handoff)
    db_session.flush()

    # Add an overdue item
    overdue_item = HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff.id,
        title="Overdue Lab",
        item_type=ItemTypeEnum.LAB_TEST,
        assigned_to=esc_user.id,
        due_date=datetime.utcnow() - timedelta(hours=2),  # Past due
        status=ItemStatusEnum.OPEN,
    )
    db_session.add(overdue_item)
    db_session.commit()

    service = EscalationService(db_session)
    events = service.check_and_escalate_overdue()

    assert len(events) >= 1
    assert any(e.handoff_id == handoff.id for e in events)
    db_session.refresh(handoff)
    assert handoff.status == HandoffStatusEnum.ESCALATED


def test_check_and_escalate_overdue_no_duplicates(db_session, esc_user, esc_patient):
    """Multiple overdue items in the same handoff produce only one escalation event."""
    handoff = Handoff(
        id=str(uuid.uuid4()),
        patient_id=esc_patient.id,
        created_by=esc_user.id,
        assigned_to=esc_user.id,
        status=HandoffStatusEnum.PENDING_REVIEW,
        priority=HandoffPriorityEnum.HIGH,
        diagnosis_summary="Unstable patient.",
        follow_up_deadline=datetime.utcnow() + timedelta(days=1),
        is_ready=True,
    )
    db_session.add(handoff)
    db_session.flush()

    for i in range(3):
        item = HandoffItem(
            id=str(uuid.uuid4()),
            handoff_id=handoff.id,
            title=f"Overdue Item {i}",
            item_type=ItemTypeEnum.MONITORING,
            assigned_to=esc_user.id,
            due_date=datetime.utcnow() - timedelta(hours=i + 1),
            status=ItemStatusEnum.OPEN,
        )
        db_session.add(item)
    db_session.commit()

    service = EscalationService(db_session)
    events = service.check_and_escalate_overdue()

    # Only one event per handoff
    handoff_event_count = sum(1 for e in events if e.handoff_id == handoff.id)
    assert handoff_event_count == 1


def test_check_and_escalate_no_overdue_items(db_session, esc_user, esc_patient):
    """When there are no overdue items, no escalation events are created."""
    handoff = Handoff(
        id=str(uuid.uuid4()),
        patient_id=esc_patient.id,
        created_by=esc_user.id,
        assigned_to=esc_user.id,
        status=HandoffStatusEnum.ACCEPTED,
        priority=HandoffPriorityEnum.LOW,
        diagnosis_summary="Patient stable.",
        follow_up_deadline=datetime.utcnow() + timedelta(days=5),
        is_ready=True,
    )
    db_session.add(handoff)
    db_session.flush()

    future_item = HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff.id,
        title="Future Lab",
        item_type=ItemTypeEnum.LAB_TEST,
        assigned_to=esc_user.id,
        due_date=datetime.utcnow() + timedelta(days=3),
        status=ItemStatusEnum.OPEN,
    )
    db_session.add(future_item)
    db_session.commit()

    service = EscalationService(db_session)
    events = service.check_and_escalate_overdue()

    assert all(e.handoff_id != handoff.id for e in events)
