"""Tests for patient endpoints."""

import pytest


# ── helpers ──────────────────────────────────────────────────────────────────

def _create_patient(client, headers, mrn="MRN-001", name="John Doe"):
    """Helper: create a patient via the API and return the JSON body."""
    response = client.post(
        "/patients",
        json={"mrn": mrn, "name": name, "date_of_birth": "1980-01-15"},
        headers=headers,
    )
    return response


# ── create patient ────────────────────────────────────────────────────────────

def test_create_patient_as_doctor(client, auth_headers):
    """A doctor can create a patient."""
    response = _create_patient(client, auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["mrn"] == "MRN-001"
    assert data["name"] == "John Doe"
    assert data["date_of_birth"] == "1980-01-15"
    assert "id" in data
    assert "created_at" in data


def test_create_patient_as_admin(client, admin_auth_headers):
    """An admin can create a patient."""
    response = _create_patient(client, admin_auth_headers)
    assert response.status_code == 201
    assert response.json()["mrn"] == "MRN-001"


def test_create_patient_as_nurse_forbidden(client, nurse_auth_headers):
    """A nurse cannot create a patient (role restricted)."""
    response = _create_patient(client, nurse_auth_headers)
    assert response.status_code == 401


def test_create_patient_unauthenticated(client):
    """Creating a patient without auth returns 403."""
    response = client.post(
        "/patients",
        json={"mrn": "MRN-002", "name": "Jane Doe"},
    )
    assert response.status_code == 403


def test_create_patient_without_date_of_birth(client, auth_headers):
    """Creating a patient without date_of_birth is valid (field is optional)."""
    response = client.post(
        "/patients",
        json={"mrn": "MRN-003", "name": "No DOB Patient"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["date_of_birth"] is None


def test_create_patient_duplicate_mrn(client, auth_headers):
    """Creating two patients with the same MRN returns 409."""
    _create_patient(client, auth_headers, mrn="DUP-MRN")
    response = _create_patient(client, auth_headers, mrn="DUP-MRN", name="Other Patient")
    assert response.status_code == 409
    assert response.json()["error"] == "MRN_ALREADY_EXISTS"


def test_create_patient_empty_mrn(client, auth_headers):
    """Creating a patient with an empty MRN returns 422."""
    response = client.post(
        "/patients",
        json={"mrn": "", "name": "Test Patient"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_patient_empty_name(client, auth_headers):
    """Creating a patient with an empty name returns 422."""
    response = client.post(
        "/patients",
        json={"mrn": "MRN-X", "name": ""},
        headers=auth_headers,
    )
    assert response.status_code == 422


# ── get patient ───────────────────────────────────────────────────────────────

def test_get_patient_success(client, auth_headers):
    """Any authenticated user can retrieve a patient by ID."""
    created = _create_patient(client, auth_headers)
    patient_id = created.json()["id"]

    response = client.get(f"/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["mrn"] == "MRN-001"


def test_get_patient_nurse_can_read(client, auth_headers, nurse_auth_headers):
    """A nurse (non-creator) can still read a patient record."""
    created = _create_patient(client, auth_headers)
    patient_id = created.json()["id"]

    response = client.get(f"/patients/{patient_id}", headers=nurse_auth_headers)
    assert response.status_code == 200


def test_get_patient_not_found(client, auth_headers):
    """Getting a non-existent patient returns 404."""
    response = client.get("/patients/nonexistent-uuid", headers=auth_headers)
    assert response.status_code == 404
    assert "PATIENT_NOT_FOUND" in response.json()["error"]


def test_get_patient_unauthenticated(client, auth_headers):
    """Getting a patient without authentication returns 403."""
    created = _create_patient(client, auth_headers)
    patient_id = created.json()["id"]

    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 403
