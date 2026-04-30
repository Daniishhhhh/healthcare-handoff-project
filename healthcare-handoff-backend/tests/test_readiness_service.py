"""Unit tests for ReadinessService – all 7 validation rules plus warnings."""

import pytest
import uuid
from datetime import datetime, timedelta

from app.services.readiness_service import ReadinessService
from app.models.handoff import Handoff, HandoffStatusEnum, HandoffPriorityEnum
from app.models.handoff_item import HandoffItem, ItemTypeEnum, ItemStatusEnum
from app.models.user import User, RoleEnum
from app.models.patient import Patient
from app.utils import hash_password


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def base_user(db_session):
    """A persisted doctor user."""
    user = User(
        id=str(uuid.uuid4()),
        email="readiness_doc@example.com",
        hashed_password=hash_password("Password123!"),
        role=RoleEnum.DOCTOR,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def base_patient(db_session, base_user):
    """A persisted patient."""
    patient = Patient(
        id=str(uuid.uuid4()),
        mrn="MRN-RS-001",
        name="Readiness Patient",
        created_by=base_user.id,
    )
    db_session.add(patient)
    db_session.commit()
    return patient


def _make_handoff(patient_id, user_id, days_ahead=7, priority=HandoffPriorityEnum.MEDIUM,
                  diagnosis="Patient stable and ready for transfer"):
    """Create an in-memory Handoff (not persisted – must be added separately)."""
    return Handoff(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        created_by=user_id,
        assigned_to=user_id,
        status=HandoffStatusEnum.DRAFT,
        priority=priority,
        diagnosis_summary=diagnosis,
        follow_up_deadline=datetime.utcnow() + timedelta(days=days_ahead),
        is_ready=False,
    )


def _make_item(handoff_id, assignee_id, item_type=ItemTypeEnum.FOLLOW_UP,
               title="Task", description=None, due_date=None):
    return HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff_id,
        title=title,
        description=description,
        item_type=item_type,
        assigned_to=assignee_id,
        due_date=due_date or (datetime.utcnow() + timedelta(days=3)),
        status=ItemStatusEnum.OPEN,
    )


# ── Rule 1: diagnosis_summary required ───────────────────────────────────────

def test_rule1_empty_diagnosis_fails(db_session, base_user, base_patient):
    """Handoff with empty diagnosis_summary fails readiness check."""
    handoff = _make_handoff(base_patient.id, base_user.id, diagnosis="")
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("Diagnosis summary is required" in f for f in result["failures"])


def test_rule1_none_diagnosis_fails(db_session, base_user, base_patient):
    """Handoff with None diagnosis_summary fails readiness check."""
    handoff = _make_handoff(base_patient.id, base_user.id, diagnosis=None)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("Diagnosis summary is required" in f for f in result["failures"])


def test_rule1_diagnosis_too_long_fails(db_session, base_user, base_patient):
    """Diagnosis summary longer than 500 characters fails."""
    long_diagnosis = "A" * 501
    handoff = _make_handoff(base_patient.id, base_user.id, diagnosis=long_diagnosis)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("500" in f for f in result["failures"])


# ── Rule 2: follow_up_deadline ────────────────────────────────────────────────

def test_rule2_missing_deadline_fails(db_session, base_user, base_patient):
    """Handoff without follow_up_deadline fails."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    handoff.follow_up_deadline = None
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("Follow-up deadline is required" in f for f in result["failures"])


def test_rule2_past_deadline_fails(db_session, base_user, base_patient):
    """Handoff with a past follow_up_deadline fails."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    handoff.follow_up_deadline = datetime.utcnow() - timedelta(hours=1)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("future" in f.lower() for f in result["failures"])


# ── Rule 3: FOLLOW_UP items must be assigned ──────────────────────────────────

def test_rule3_unassigned_follow_up_fails(db_session, base_user, base_patient):
    """Handoff with an unassigned FOLLOW_UP item (empty assigned_to) fails."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    # Use empty string to simulate an unassigned item (NOT NULL prevents actual NULL)
    item = HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff.id,
        title="Unassigned Follow-up",
        item_type=ItemTypeEnum.FOLLOW_UP,
        assigned_to="",
        due_date=datetime.utcnow() + timedelta(days=2),
        status=ItemStatusEnum.OPEN,
    )
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("follow-up" in f.lower() and "unassigned" in f.lower() for f in result["failures"])


# ── Rule 4: MEDICATION items need rationale ≥20 chars ────────────────────────

def test_rule4_medication_no_description_fails(db_session, base_user, base_patient):
    """A MEDICATION item with no description fails readiness."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MEDICATION,
                      title="Amoxicillin", description=None)
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("Amoxicillin" in f and "rationale" in f.lower() for f in result["failures"])


def test_rule4_medication_short_description_fails(db_session, base_user, base_patient):
    """A MEDICATION item with a description shorter than 20 chars fails."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MEDICATION,
                      title="Metformin", description="Short desc")  # < 20 chars
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("Metformin" in f for f in result["failures"])


def test_rule4_medication_with_sufficient_rationale_passes(db_session, base_user, base_patient):
    """A MEDICATION item with description ≥20 chars passes rule 4."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MEDICATION,
                      title="Lisinopril",
                      description="Prescribed for blood pressure control - 10mg daily")
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)
    # Rule 4 itself should not produce a failure
    assert not any("Lisinopril" in f for f in result["failures"])


# ── Rule 5: LAB_TEST items must have due_date ─────────────────────────────────

def test_rule5_lab_test_no_due_date_fails(db_session, base_user, base_patient):
    """A LAB_TEST item without a due_date fails readiness."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff.id,
        title="CBC Panel",
        item_type=ItemTypeEnum.LAB_TEST,
        assigned_to=base_user.id,
        due_date=None,
        status=ItemStatusEnum.OPEN,
    )
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("lab test" in f.lower() and "due date" in f.lower() for f in result["failures"])


# ── Rule 6: CRITICAL priority – all items assigned ───────────────────────────

def test_rule6_critical_unassigned_item_fails(db_session, base_user, base_patient):
    """A CRITICAL handoff with an item with empty assigned_to fails readiness."""
    handoff = _make_handoff(base_patient.id, base_user.id,
                            priority=HandoffPriorityEnum.CRITICAL)
    db_session.add(handoff)
    db_session.flush()

    # Use empty string to simulate an unassigned item
    item = HandoffItem(
        id=str(uuid.uuid4()),
        handoff_id=handoff.id,
        title="Unowned Item",
        item_type=ItemTypeEnum.MONITORING,
        assigned_to="",
        due_date=datetime.utcnow() + timedelta(days=2),
        status=ItemStatusEnum.OPEN,
    )
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("CRITICAL" in f and "unassigned" in f.lower() for f in result["failures"])


def test_rule6_critical_all_assigned_passes(db_session, base_user, base_patient):
    """A CRITICAL handoff with all items properly assigned passes rule 6."""
    handoff = _make_handoff(base_patient.id, base_user.id,
                            priority=HandoffPriorityEnum.CRITICAL)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MONITORING)
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert not any("CRITICAL" in f and "unassigned" in f.lower() for f in result["failures"])


# ── Rule 7: No vague language ─────────────────────────────────────────────────

@pytest.mark.parametrize("phrase", [
    "check soon",
    "review later",
    "monitor closely",
    "as needed",
    "prn",
    "asap",
    "when possible",
    "follow up soon",
    "check later",
    "see how it goes",
])
def test_rule7_vague_phrase_in_diagnosis_fails(db_session, base_user, base_patient, phrase):
    """Vague language in diagnosis_summary fails readiness."""
    diagnosis = f"Patient is stable, {phrase}, and should recover."
    handoff = _make_handoff(base_patient.id, base_user.id, diagnosis=diagnosis)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any(phrase in f.lower() for f in result["failures"])


def test_rule7_vague_language_in_item_description_fails(db_session, base_user, base_patient):
    """Vague language in item description fails readiness."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id,
                      title="Consult Cardiology",
                      description="Refer to cardiology asap for evaluation")
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is False
    assert any("asap" in f.lower() for f in result["failures"])


# ── All checks passing ────────────────────────────────────────────────────────

def test_all_checks_pass_with_no_items(db_session, base_user, base_patient):
    """A handoff with valid diagnosis and future deadline (no items) passes."""
    handoff = _make_handoff(
        base_patient.id, base_user.id,
        diagnosis="Patient has controlled hypertension. BP 130/80 on Lisinopril 10mg.",
        days_ahead=10,
    )
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is True
    assert result["failures"] == []


def test_all_checks_pass_with_items(db_session, base_user, base_patient):
    """A handoff with valid items of all types passes when all rules are satisfied."""
    handoff = _make_handoff(
        base_patient.id, base_user.id,
        diagnosis="Patient recovering from acute pneumonia. Antibiotics completed.",
        days_ahead=14,
    )
    db_session.add(handoff)
    db_session.flush()

    # Valid LAB_TEST item (has due_date)
    lab = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.LAB_TEST,
                     title="Chest X-ray", due_date=datetime.utcnow() + timedelta(days=2))
    # Valid MEDICATION item (description ≥ 20 chars)
    med = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MEDICATION,
                     title="Amoxicillin 500mg",
                     description="Continue for 7 days to complete course of antibiotics",
                     due_date=datetime.utcnow() + timedelta(days=7))
    # Valid FOLLOW_UP item (assigned)
    follow = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.FOLLOW_UP,
                        title="GP Follow-up")

    db_session.add_all([lab, med, follow])
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert result["is_ready"] is True
    assert result["failures"] == []


# ── Warnings ──────────────────────────────────────────────────────────────────

def test_warning_no_items(db_session, base_user, base_patient):
    """Handoff with no items gets a 'no items' warning (non-blocking)."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert any("no items" in w.lower() for w in result["warnings"])


def test_warning_open_items(db_session, base_user, base_patient):
    """Handoff with open items gets a warning about open items."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.flush()

    item = _make_item(handoff.id, base_user.id, item_type=ItemTypeEnum.MONITORING)
    db_session.add(item)
    db_session.commit()

    service = ReadinessService(db_session)
    result = service.validate_handoff(handoff)

    assert any("open" in w.lower() for w in result["warnings"])


# ── assert_ready ──────────────────────────────────────────────────────────────

def test_assert_ready_raises_when_not_ready(db_session, base_user, base_patient):
    """assert_ready raises HandoffNotReady when validation fails."""
    from app.exceptions import HandoffNotReady

    handoff = _make_handoff(base_patient.id, base_user.id, diagnosis="")
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    with pytest.raises(HandoffNotReady):
        service.assert_ready(handoff)


def test_assert_ready_does_not_raise_when_ready(db_session, base_user, base_patient):
    """assert_ready does not raise when handoff passes all checks."""
    handoff = _make_handoff(
        base_patient.id, base_user.id,
        diagnosis="Hypertension controlled. Discharged on Lisinopril 10mg.",
    )
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    service.assert_ready(handoff)  # Should not raise


# ── get_readiness_summary ─────────────────────────────────────────────────────

def test_get_readiness_summary_structure(db_session, base_user, base_patient):
    """get_readiness_summary returns expected keys."""
    handoff = _make_handoff(base_patient.id, base_user.id)
    db_session.add(handoff)
    db_session.commit()

    service = ReadinessService(db_session)
    summary = service.get_readiness_summary(handoff)

    assert "handoff_id" in summary
    assert "is_ready" in summary
    assert "total_items" in summary
    assert "items_by_status" in summary
    assert "failures" in summary
    assert "warnings" in summary
    assert "checked_at" in summary
    assert summary["handoff_id"] == handoff.id
    assert summary["items_by_status"]["open"] == 0
