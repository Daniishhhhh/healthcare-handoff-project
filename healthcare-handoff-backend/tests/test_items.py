"""Tests for handoff item endpoints."""

import pytest
from datetime import datetime, timedelta


# ── helpers ──────────────────────────────────────────────────────────────────

def _future(days: int = 14) -> str:
    return (datetime.utcnow() + timedelta(days=days)).isoformat()


def _signup_and_login(client, email: str, role: str, password: str = "DoctorPass123!"):
    client.post("/auth/signup", json={"email": email, "password": password, "role": role})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_patient(client, headers, mrn="MRN-ITEM001"):
    resp = client.post(
        "/patients",
        json={"mrn": mrn, "name": "Item Test Patient"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_handoff(client, headers, patient_id, assignee_id):
    resp = client.post(
        "/handoffs",
        json={
            "patient_id": patient_id,
            "assigned_to": assignee_id,
            "priority": "MEDIUM",
            "diagnosis_summary": "Stable patient awaiting discharge.",
            "follow_up_deadline": _future(days=7),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _add_item(client, headers, handoff_id, assignee_id, item_type="FOLLOW_UP", title="Follow up"):
    return client.post(
        f"/handoffs/{handoff_id}/items",
        json={
            "title": title,
            "description": "Please schedule follow-up appointment.",
            "item_type": item_type,
            "assigned_to": assignee_id,
            "due_date": _future(),
        },
        headers=headers,
    )


# ── add item ──────────────────────────────────────────────────────────────────

def test_add_item_to_handoff(client):
    """An authenticated user can add an item to a handoff."""
    creator_headers = _signup_and_login(client, "item_creator1@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee1@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT1")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = _add_item(client, creator_headers, handoff_id, assignee_id)
    assert resp.status_code == 201
    data = resp.json()
    assert data["handoff_id"] == handoff_id
    assert data["title"] == "Follow up"
    assert data["item_type"] == "FOLLOW_UP"
    assert data["status"] == "OPEN"
    assert "id" in data


def test_add_item_all_types(client):
    """Items can be added for each valid item type."""
    creator_headers = _signup_and_login(client, "item_creator2@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee2@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT2")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    for item_type in ["LAB_TEST", "MEDICATION", "FOLLOW_UP", "MONITORING", "CONSULTATION", "OTHER"]:
        resp = _add_item(client, creator_headers, handoff_id, assignee_id,
                         item_type=item_type, title=f"Item {item_type}")
        assert resp.status_code == 201, f"Failed for type {item_type}"
        assert resp.json()["item_type"] == item_type


def test_add_item_nonexistent_handoff(client):
    """Adding an item to a non-existent handoff returns 404."""
    creator_headers = _signup_and_login(client, "item_creator3@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee3@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]

    resp = _add_item(client, creator_headers, "nonexistent-handoff", assignee_id)
    assert resp.status_code == 404


def test_add_item_nonexistent_assignee(client):
    """Adding an item with a non-existent assignee returns 404."""
    creator_headers = _signup_and_login(client, "item_creator4@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee4@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT4")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = _add_item(client, creator_headers, handoff_id, "nonexistent-user-id")
    assert resp.status_code == 404


def test_add_item_unauthenticated(client):
    """Adding an item without auth returns 403."""
    resp = client.post("/handoffs/some-id/items", json={})
    assert resp.status_code == 403


# ── list items ────────────────────────────────────────────────────────────────

def test_list_items_empty(client):
    """Listing items on a new handoff returns an empty list."""
    creator_headers = _signup_and_login(client, "item_creator5@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee5@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT5")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = client.get(f"/handoffs/{handoff_id}/items", headers=creator_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_id"] == handoff_id
    assert data["item_count"] == 0
    assert data["items"] == []


def test_list_items_returns_all(client):
    """Listing items returns all items added to the handoff."""
    creator_headers = _signup_and_login(client, "item_creator6@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee6@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT6")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    _add_item(client, creator_headers, handoff_id, assignee_id, title="Item A")
    _add_item(client, creator_headers, handoff_id, assignee_id, title="Item B")

    resp = client.get(f"/handoffs/{handoff_id}/items", headers=creator_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["item_count"] == 2
    titles = [i["title"] for i in data["items"]]
    assert "Item A" in titles
    assert "Item B" in titles


def test_list_items_unauthorized_user_forbidden(client):
    """An unrelated user cannot list items in a handoff."""
    creator_headers = _signup_and_login(client, "item_creator7@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee7@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    unrelated_headers = _signup_and_login(client, "item_unrelated7@example.com", "doctor")
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT7")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = client.get(f"/handoffs/{handoff_id}/items", headers=unrelated_headers)
    assert resp.status_code == 403


# ── get specific item ─────────────────────────────────────────────────────────

def test_get_specific_item(client):
    """Retrieve a specific item by ID within a handoff."""
    creator_headers = _signup_and_login(client, "item_creator8@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee8@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT8")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)
    item_id = _add_item(client, creator_headers, handoff_id, assignee_id,
                        title="Specific Item").json()["id"]

    resp = client.get(f"/handoffs/{handoff_id}/items/{item_id}", headers=creator_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id
    assert resp.json()["title"] == "Specific Item"


def test_get_item_not_found(client):
    """Getting a non-existent item returns 404."""
    creator_headers = _signup_and_login(client, "item_creator9@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee9@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT9")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = client.get(f"/handoffs/{handoff_id}/items/nonexistent-item", headers=creator_headers)
    assert resp.status_code == 404


def test_get_item_wrong_handoff(client):
    """Getting an item with the wrong handoff_id returns 404."""
    creator_headers = _signup_and_login(client, "item_creator10@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee10@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT10")
    handoff_id_a = _create_handoff(client, creator_headers, patient_id, assignee_id)
    patient_id_b = _create_patient(client, creator_headers, mrn="MRN-IT10B")
    handoff_id_b = _create_handoff(client, creator_headers, patient_id_b, assignee_id)

    item_id = _add_item(client, creator_headers, handoff_id_a, assignee_id,
                        title="Item in A").json()["id"]

    # Try to access item from handoff A using handoff B's URL
    resp = client.get(f"/handoffs/{handoff_id_b}/items/{item_id}", headers=creator_headers)
    assert resp.status_code == 404


# ── update item status ────────────────────────────────────────────────────────

def test_update_item_status_to_in_progress(client):
    """Update item status from OPEN to IN_PROGRESS."""
    creator_headers = _signup_and_login(client, "item_creator11@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee11@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT11")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)
    item_id = _add_item(client, creator_headers, handoff_id, assignee_id).json()["id"]

    resp = client.patch(
        f"/handoffs/{handoff_id}/items/{item_id}",
        json={"status": "IN_PROGRESS"},
        headers=creator_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"


def test_update_item_status_to_completed(client):
    """Update item status to COMPLETED sets completed_at timestamp."""
    creator_headers = _signup_and_login(client, "item_creator12@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee12@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT12")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)
    item_id = _add_item(client, creator_headers, handoff_id, assignee_id).json()["id"]

    resp = client.patch(
        f"/handoffs/{handoff_id}/items/{item_id}",
        json={"status": "COMPLETED"},
        headers=creator_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "COMPLETED"
    assert data["completed_at"] is not None


def test_update_item_status_invalid(client):
    """Updating item with an invalid status returns 409."""
    creator_headers = _signup_and_login(client, "item_creator13@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee13@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT13")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)
    item_id = _add_item(client, creator_headers, handoff_id, assignee_id).json()["id"]

    resp = client.patch(
        f"/handoffs/{handoff_id}/items/{item_id}",
        json={"status": "CANCELLED"},
        headers=creator_headers,
    )
    assert resp.status_code == 409


def test_update_item_nonexistent(client):
    """Updating a non-existent item returns 404."""
    creator_headers = _signup_and_login(client, "item_creator14@example.com", "doctor")
    assignee_signup = client.post(
        "/auth/signup",
        json={"email": "item_assignee14@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    assignee_id = assignee_signup.json()["id"]
    patient_id = _create_patient(client, creator_headers, mrn="MRN-IT14")
    handoff_id = _create_handoff(client, creator_headers, patient_id, assignee_id)

    resp = client.patch(
        f"/handoffs/{handoff_id}/items/nonexistent-item",
        json={"status": "IN_PROGRESS"},
        headers=creator_headers,
    )
    assert resp.status_code == 404
