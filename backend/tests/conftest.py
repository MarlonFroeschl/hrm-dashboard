"""Shared test fixtures: in-memory SQLite DB, auth overrides, external service mocks."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import JSON, String, create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# ---------------------------------------------------------------------------
# SQLite type compatibility – remap PG-only types once per process
# ---------------------------------------------------------------------------

_TYPES_REMAPPED = False


def _remap_pg_types_for_sqlite() -> None:
    global _TYPES_REMAPPED
    if _TYPES_REMAPPED:
        return
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, PG_UUID):
                col.type = String(36)
            elif isinstance(col.type, JSONB):
                col.type = JSON()
    _TYPES_REMAPPED = True


def _make_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _record):  # type: ignore[misc]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_engine():
    _remap_pg_types_for_sqlite()
    engine = _make_engine()
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:  # type: ignore[type-arg]
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    token = create_access_token(subject="test-user@example.com")
    return {"Authorization": f"Bearer {token}"}


async def _stub_get_current_user() -> str:
    return "test-user@example.com"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _stub_get_current_user

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test-data helpers
# ---------------------------------------------------------------------------

APPLICANT_PAYLOAD: dict[str, Any] = {
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada.lovelace@example.com",
    "phone": "+43 699 12345678",
}


@pytest.fixture()
def created_applicant(client: TestClient) -> dict[str, Any]:
    resp = client.post("/api/v1/applicants/", json=APPLICANT_PAYLOAD)
    assert resp.status_code == 201, resp.text
    return resp.json()  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# External-service mocks
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_cv_parser():
    from app.schemas.applicant import CVExtractedData

    fake_data = CVExtractedData(
        skills=["Python", "FastAPI", "Docker"],
        roles=["Backend Engineer"],
        contact_info={"name": "Ada Lovelace", "email": "ada@example.com", "phone": ""},
    )
    with patch(
        "app.services.applicant_service.cv_parser_service.parse_cv",
        new_callable=AsyncMock,
        return_value=("raw cv text", fake_data, 75.0),
    ) as mock:
        yield mock


@pytest.fixture()
def mock_webhook():
    with patch(
        "app.services.applicant_service.webhook_service.trigger",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock:
        yield mock


@pytest.fixture()
def mock_file_write():
    with patch(
        "app.services.applicant_service.asyncio.to_thread",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock:
        yield mock
