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


def test_login_success(auth_headers):
    """Test successful login."""
    assert "Authorization" in auth_headers


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


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/auth/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"