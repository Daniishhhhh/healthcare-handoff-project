"""Tests for auth endpoints."""

import pytest


def test_signup_success(client):
    """Test successful user signup."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "john@example.com",
            "password": "SecurePass123!",
            "role": "nurse",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@example.com"
    assert data["role"] == "nurse"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_signup_all_roles(client):
    """Test signup with each valid role."""
    roles = ["intern", "nurse", "doctor", "admin"]
    for role in roles:
        response = client.post(
            "/auth/signup",
            json={
                "email": f"{role}@example.com",
                "password": "SecurePass123!",
                "role": role,
            },
        )
        assert response.status_code == 201, f"Role {role} failed"
        assert response.json()["role"] == role


def test_signup_duplicate_email(client):
    """Test signup with duplicate email."""
    client.post(
        "/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "role": "nurse",
        },
    )

    response = client.post(
        "/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "role": "doctor",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_ALREADY_EXISTS"


def test_signup_weak_password_no_uppercase(client):
    """Test signup with password missing uppercase letter."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "weakpass@example.com",
            "password": "weakpassword123!",
            "role": "nurse",
        },
    )
    assert response.status_code == 400


def test_signup_weak_password_no_digit(client):
    """Test signup with password missing digit."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "weakpass2@example.com",
            "password": "WeakPassword!!!",
            "role": "nurse",
        },
    )
    assert response.status_code == 400


def test_signup_weak_password_no_special_char(client):
    """Test signup with password missing special character."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "weakpass3@example.com",
            "password": "WeakPassword123",
            "role": "nurse",
        },
    )
    assert response.status_code == 400


def test_signup_password_too_short(client):
    """Test signup with password that is too short (< 12 chars)."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "shortpass@example.com",
            "password": "Short1!",
            "role": "nurse",
        },
    )
    assert response.status_code == 422


def test_signup_invalid_role(client):
    """Test signup with invalid role."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "badrole@example.com",
            "password": "SecurePass123!",
            "role": "superadmin",
        },
    )
    assert response.status_code == 422


def test_signup_invalid_email_format(client):
    """Test signup with malformed email."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "not-an-email",
            "password": "SecurePass123!",
            "role": "nurse",
        },
    )
    assert response.status_code == 422


def test_login_success(auth_headers):
    """Test successful login returns auth header."""
    assert "Authorization" in auth_headers
    assert auth_headers["Authorization"].startswith("Bearer ")


def test_login_returns_token_details(client):
    """Test that login response includes token details and user info."""
    client.post(
        "/auth/signup",
        json={"email": "tokentest@example.com", "password": "SecurePass123!", "role": "doctor"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "tokentest@example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["user"]["email"] == "tokentest@example.com"
    assert data["user"]["role"] == "doctor"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


def test_login_wrong_password(client):
    """Test login with correct email but wrong password."""
    client.post(
        "/auth/signup",
        json={"email": "rightuser@example.com", "password": "CorrectPass123!", "role": "nurse"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "rightuser@example.com", "password": "WrongPass123!"},
    )
    assert response.status_code == 401


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/auth/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data