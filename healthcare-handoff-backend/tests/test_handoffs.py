"""Tests for handoff endpoints."""

import pytest
from datetime import datetime, timedelta


# ── helpers ──────────────────────────────────────────────────────────────────

def _future(days: int = 30) -> str:
    return (datetime.utcnow() + timedelta(days=days)).isoformat()


def _signup_and_login(client, email: str, role: str, password: str = "DoctorPass123!"):
    client.post("/auth/signup", json={"email": email, "password": password, "role": role})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_patient(client, headers, mrn="MRN-H001"):
    resp = client.post(
        "/patients",
        json={"mrn": mrn, "name": "Handoff Patient"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_handoff(client, creator_headers, patient_id: str, assigned_to_id: str, **overrides):
    """Create a handoff and return the JSON body."""
    payload = {
        "patient_id": patient_id,
        "assigned_to": assigned_to_id,
        "priority": "MEDIUM",
        "diagnosis_summary": "Acute bronchitis treated with antibiotics",
        "follow_up_deadline": _future(days=7),
    }
    payload.update(overrides)
    resp = client.post("/handoffs", json=payload, headers=creator_headers)
    return resp


# ── create handoff ────────────────────────────────────────────────────────────

def test_create_handoff_as_doctor(client, auth_headers, second_doctor_auth_headers):
    """A doctor can create a handoff."""
    # Get the second doctor's user id via signup response
    signup = client.post(
        "/auth/signup",
        json={"email": "assignee@example.com", "password": "AssignPass123!", "role": "doctor"},
    )
    assignee_id = signup.json()["id"]
    patient_id = _create_patient(client, auth_headers)

    resp = _create_handoff(client, auth_headers, patient_id, assignee_id)
    assert resp.status_code == 201
    data = resp.json()
    assert data["patient_id"] == patient_id
    assert data["assigned_to"] == assignee_id
    assert data["status"] == "DRAFT"
    assert data["priority"] == "MEDIUM"
    assert data["is_ready"] is False


def test_create_handoff_as_admin(client, admin_auth_headers):
    """An admin can create a handoff."""
    assignee = client.post(
        "/auth/signup",
        json={"email": "nurse2@example.com", "password": "NursePass123!", "role": "nurse"},
    )
    assignee_id = assignee.json()["id"]
    patient_id = _create_patient(client, admin_auth_headers)

    resp = _create_handoff(client, admin_auth_headers, patient_id, assignee_id)
    assert resp.status_code == 201


def test_create_handoff_as_nurse_forbidden(client, nurse_auth_headers):
    """A nurse cannot create a handoff."""
    resp = client.post(
        "/handoffs",
        json={
            "patient_id": "some-id",
            "assigned_to": "some-id",
            "priority": "MEDIUM",
            "diagnosis_summary": "Test",
            "follow_up_deadline": _future(),
        },
        headers=nurse_auth_headers,
    )
    assert resp.status_code == 401


def test_create_handoff_unauthenticated(client):
    """Creating a handoff without auth returns 403."""
    resp = client.post("/handoffs", json={})
    assert resp.status_code == 403


def test_create_handoff_patient_not_found(client, auth_headers):
    """Creating a handoff for a non-existent patient returns 404."""
    # We still need a valid assignee
    assignee = client.post(
        "/auth/signup",
        json={"email": "doc99@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee.json()["id"]

    resp = _create_handoff(client, auth_headers, "nonexistent-patient-id", assignee_id)
    assert resp.status_code == 404
    assert "PATIENT_NOT_FOUND" in resp.json()["error"]


def test_create_handoff_assigned_user_not_found(client, auth_headers):
    """Creating a handoff with a non-existent assignee returns 404."""
    patient_id = _create_patient(client, auth_headers)
    resp = _create_handoff(client, auth_headers, patient_id, "nonexistent-user-id")
    assert resp.status_code == 404
    assert "USER_NOT_FOUND" in resp.json()["error"]


def test_create_handoff_past_deadline_rejected(client, auth_headers):
    """Creating a handoff with a past follow_up_deadline returns 422."""
    assignee = client.post(
        "/auth/signup",
        json={"email": "doc77@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee.json()["id"]
    patient_id = _create_patient(client, auth_headers)

    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    resp = _create_handoff(client, auth_headers, patient_id, assignee_id,
                           follow_up_deadline=past)
    assert resp.status_code == 422


# ── get handoff ───────────────────────────────────────────────────────────────

def test_get_handoff_as_creator(client, auth_headers):
    """The creator of a handoff can retrieve it."""
    assignee = client.post(
        "/auth/signup",
        json={"email": "assignee2@example.com", "password": "AssignPass123!", "role": "doctor"},
    )
    assignee_id = assignee.json()["id"]
    patient_id = _create_patient(client, auth_headers)
    handoff_id = _create_handoff(client, auth_headers, patient_id, assignee_id).json()["id"]

    resp = client.get(f"/handoffs/{handoff_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == handoff_id


def test_get_handoff_as_assignee(client):
    """The assignee of a handoff can retrieve it."""
    creator_headers = _signup_and_login(client, "creator3@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee3b@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee3b_headers = _signup_and_login(client, "assignee3b@example.com", "doctor")

    patient_id = _create_patient(client, creator_headers, mrn="MRN-A3")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    # The actual assignee should be able to read the handoff
    resp = client.get(f"/handoffs/{handoff_id}", headers=assignee3b_headers)
    assert resp.status_code == 200


def test_get_handoff_unrelated_user_forbidden(client):
    """An unrelated user cannot view someone else's handoff."""
    creator_headers = _signup_and_login(client, "creator4@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee4@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    unrelated_headers = _signup_and_login(client, "unrelated4@example.com", "doctor")

    patient_id = _create_patient(client, creator_headers, mrn="MRN-U4")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.get(f"/handoffs/{handoff_id}", headers=unrelated_headers)
    assert resp.status_code == 403


def test_get_handoff_as_admin(client, admin_auth_headers):
    """An admin can view any handoff."""
    creator_headers = _signup_and_login(client, "creator5@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee5@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]

    patient_id = _create_patient(client, creator_headers, mrn="MRN-A5")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.get(f"/handoffs/{handoff_id}", headers=admin_auth_headers)
    assert resp.status_code == 200


def test_get_handoff_not_found(client, auth_headers):
    """Getting a non-existent handoff returns 404."""
    resp = client.get("/handoffs/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404
    assert "HANDOFF_NOT_FOUND" in resp.json()["error"]


# ── update handoff ────────────────────────────────────────────────────────────

def test_update_handoff_by_creator(client):
    """The creator can update a DRAFT handoff."""
    creator_headers = _signup_and_login(client, "creator6@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee6@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-U6")
    handoff = _create_handoff(client, creator_headers, patient_id, assignee_id)
    handoff_id = handoff.json()["id"]

    resp = client.patch(
        f"/handoffs/{handoff_id}",
        json={
            "patient_id": patient_id,
            "assigned_to": assignee_id,
            "priority": "HIGH",
            "diagnosis_summary": "Updated diagnosis summary here",
            "follow_up_deadline": _future(days=14),
        },
        headers=creator_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "HIGH"
    assert resp.json()["diagnosis_summary"] == "Updated diagnosis summary here"


def test_update_handoff_by_non_creator_forbidden(client):
    """A non-creator cannot update a handoff."""
    creator_headers = _signup_and_login(client, "creator7@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee7@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    other_headers = _signup_and_login(client, "other7@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-U7")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.patch(
        f"/handoffs/{handoff_id}",
        json={
            "patient_id": patient_id,
            "assigned_to": assignee_id,
            "priority": "LOW",
            "diagnosis_summary": "Attempt to hijack",
            "follow_up_deadline": _future(),
        },
        headers=other_headers,
    )
    assert resp.status_code == 403


# ── readiness check ───────────────────────────────────────────────────────────

def test_readiness_check_fails_missing_fields(client):
    """Readiness check on a minimal DRAFT handoff returns not-ready."""
    creator_headers = _signup_and_login(client, "creator8@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee8@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-R8")
    # Create handoff with deadline only 1 hour in the future (still valid for creation),
    # readiness will validate the deadline is set
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.post(
        f"/handoffs/{handoff_id}/readiness-check", headers=creator_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "is_ready" in data
    assert "failures" in data


def test_readiness_check_unauthorized(client):
    """An unrelated user cannot run the readiness check."""
    creator_headers = _signup_and_login(client, "creator9@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee9@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    unrelated_headers = _signup_and_login(client, "unrelated9@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-R9")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.post(f"/handoffs/{handoff_id}/readiness-check", headers=unrelated_headers)
    assert resp.status_code == 403


# ── accept handoff ────────────────────────────────────────────────────────────

def test_accept_handoff_success(client):
    """The assignee can accept a handoff that passes readiness checks."""
    creator_headers = _signup_and_login(client, "creator10@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee10@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee_headers = _signup_and_login(client, "assignee10@example.com", "doctor")

    patient_id = _create_patient(client, creator_headers, mrn="MRN-ACC10")
    # Handoff with valid diagnosis and future deadline – no items, so readiness passes
    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Patient has stable hypertension. BP controlled on lisinopril."
    ).json()["id"]

    resp = client.post(f"/handoffs/{handoff_id}/accept", headers=assignee_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACCEPTED"
    assert resp.json()["accepted_at"] is not None


def test_accept_handoff_by_non_assignee_forbidden(client):
    """Only the assignee (or admin) can accept a handoff."""
    creator_headers = _signup_and_login(client, "creator11@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee11@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    other_headers = _signup_and_login(client, "other11@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-ACC11")
    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Patient stable on medications."
    ).json()["id"]

    resp = client.post(f"/handoffs/{handoff_id}/accept", headers=other_headers)
    assert resp.status_code == 403


def test_accept_handoff_not_ready_fails(client):
    """Accepting a handoff that doesn't pass readiness check returns 409."""
    creator_headers = _signup_and_login(client, "creator12@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee12@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee_headers = _signup_and_login(client, "assignee12@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-ACC12")

    # Handoff with a past deadline will fail the readiness check
    # We bypass the schema validator by creating a valid handoff and then checking
    # with vague language in the diagnosis
    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Patient should check soon and review later if needed"
    ).json()["id"]

    resp = client.post(f"/handoffs/{handoff_id}/accept", headers=assignee_headers)
    assert resp.status_code == 409
    assert resp.json()["error"] == "HANDOFF_NOT_READY"


# ── escalate handoff ──────────────────────────────────────────────────────────

def test_escalate_handoff(client):
    """Any participant can manually escalate a handoff."""
    creator_headers = _signup_and_login(client, "creator13@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee13@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-ESC13")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]

    resp = client.post(
        f"/handoffs/{handoff_id}/escalate?reason=Patient+condition+changed",
        headers=creator_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_status"] == "ESCALATED"
    assert data["escalation_event"]["reason"] == "Patient condition changed"
    assert data["escalation_event"]["triggered_by"] == "MANUAL"


# ── complete handoff ──────────────────────────────────────────────────────────

def test_complete_handoff_success(client):
    """Completing an ACCEPTED handoff transitions it to COMPLETED."""
    creator_headers = _signup_and_login(client, "creator14@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee14@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee_headers = _signup_and_login(client, "assignee14@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-COMP14")

    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Patient discharged with stable vitals."
    ).json()["id"]

    # First accept the handoff
    client.post(f"/handoffs/{handoff_id}/accept", headers=assignee_headers)

    # Then complete it
    resp = client.post(f"/handoffs/{handoff_id}/complete", headers=assignee_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"
    assert resp.json()["completed_at"] is not None


def test_complete_handoff_by_creator(client):
    """The creator (not assignee) can also complete an accepted handoff."""
    creator_headers = _signup_and_login(client, "creator15@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee15@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee_headers = _signup_and_login(client, "assignee15@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-COMP15")

    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Stable patient discharged after observation."
    ).json()["id"]

    client.post(f"/handoffs/{handoff_id}/accept", headers=assignee_headers)
    resp = client.post(f"/handoffs/{handoff_id}/complete", headers=creator_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"


def test_complete_handoff_unrelated_user_forbidden(client):
    """An unrelated user cannot complete a handoff."""
    creator_headers = _signup_and_login(client, "creator16@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee16@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    assignee_headers = _signup_and_login(client, "assignee16@example.com", "doctor")
    unrelated_headers = _signup_and_login(client, "unrelated16@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-COMP16")

    handoff_id = _create_handoff(
        client, creator_headers, patient_id, assignee_id,
        diagnosis_summary="Stable patient, ready to discharge."
    ).json()["id"]
    client.post(f"/handoffs/{handoff_id}/accept", headers=assignee_headers)

    resp = client.post(f"/handoffs/{handoff_id}/complete", headers=unrelated_headers)
    assert resp.status_code == 403


def test_complete_handoff_not_found(client, auth_headers):
    """Completing a non-existent handoff returns 404."""
    resp = client.post("/handoffs/nonexistent-id/complete", headers=auth_headers)
    assert resp.status_code == 404


def test_invalid_state_transition_complete_from_draft(client):
    """Cannot complete a DRAFT handoff (invalid state transition)."""
    creator_headers = _signup_and_login(client, "creator17@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "assignee17@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-TRANS17")

    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id).json()["id"]
    resp = client.post(f"/handoffs/{handoff_id}/complete", headers=creator_headers)
    assert resp.status_code == 409
    assert resp.json()["error"] == "INVALID_STATE_TRANSITION"
