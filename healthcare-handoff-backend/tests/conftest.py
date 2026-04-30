"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from app.db.database import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session):
    """Create test client with overridden dependencies."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Create a test doctor user and return auth headers."""
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "doctor",
        },
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def nurse_auth_headers(client):
    """Create a nurse user and return auth headers."""
    client.post(
        "/auth/signup",
        json={"email": "nurse@example.com", "password": "NursePass123!", "role": "nurse"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "nurse@example.com", "password": "NursePass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client):
    """Create an admin user and return auth headers."""
    client.post(
        "/auth/signup",
        json={"email": "admin@example.com", "password": "AdminPass123!", "role": "admin"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "AdminPass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_doctor_auth_headers(client):
    """Create a second doctor user and return auth headers."""
    client.post(
        "/auth/signup",
        json={"email": "doctor2@example.com", "password": "DoctorPass123!", "role": "doctor"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "doctor2@example.com", "password": "DoctorPass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}