"""Tests for the applicant ingestion API (46 test cases).

Endpoints covered:
  POST   /api/v1/applicants/
  POST   /api/v1/applicants/upload-cv
  GET    /api/v1/applicants/
  GET    /api/v1/applicants/{id}
  PATCH  /api/v1/applicants/{id}/status
  POST   /api/v1/applicants/{id}/invite
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import APPLICANT_PAYLOAD, _stub_get_current_user

_BASE = "/api/v1/applicants"


def _url(suffix: str = "") -> str:
    return f"{_BASE}{suffix}"


def _restore_auth_override() -> None:
    from app.api.v1.dependencies import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = _stub_get_current_user


# ===========================================================================
# POST /api/v1/applicants/
# ===========================================================================


class TestCreateApplicant:
    def test_returns_201_for_valid_payload(self, client: TestClient) -> None:
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        assert resp.status_code == 201

    def test_persists_fields_correctly(self, client: TestClient) -> None:
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        body: dict[str, Any] = resp.json()
        assert body["first_name"] == APPLICANT_PAYLOAD["first_name"]
        assert body["last_name"] == APPLICANT_PAYLOAD["last_name"]
        assert body["email"] == APPLICANT_PAYLOAD["email"]
        assert body["phone"] == APPLICANT_PAYLOAD["phone"]

    def test_sets_status_to_active(self, client: TestClient) -> None:
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        assert resp.json()["status"] == "active"

    def test_sets_person_type_to_applicant(self, client: TestClient) -> None:
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        assert resp.json()["person_type"] == "applicant"

    def test_returns_valid_uuid_id(self, client: TestClient) -> None:
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        uuid.UUID(resp.json()["id"])

    def test_returns_409_on_duplicate_email(self, client: TestClient) -> None:
        client.post(_url("/"), json=APPLICANT_PAYLOAD)
        resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
        assert resp.status_code == 409

    def test_returns_422_when_email_missing(self, client: TestClient) -> None:
        payload = {k: v for k, v in APPLICANT_PAYLOAD.items() if k != "email"}
        assert client.post(_url("/"), json=payload).status_code == 422

    def test_returns_422_when_email_invalid(self, client: TestClient) -> None:
        payload = {**APPLICANT_PAYLOAD, "email": "not-an-email"}
        assert client.post(_url("/"), json=payload).status_code == 422

    def test_returns_401_without_auth_header(self, client: TestClient) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            resp = client.post(_url("/"), json=APPLICANT_PAYLOAD)
            assert resp.status_code == 401
        finally:
            _restore_auth_override()


# ===========================================================================
# POST /api/v1/applicants/upload-cv
# ===========================================================================


class TestUploadCV:
    def test_returns_202_for_valid_pdf(
        self,
        client: TestClient,
        created_applicant: dict[str, Any],
        mock_cv_parser,
        mock_webhook,
        mock_file_write,
    ) -> None:
        resp = client.post(
            _url("/upload-cv"),
            params={"person_id": created_applicant["id"]},
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert resp.status_code == 202

    def test_returns_document_id_in_body(
        self,
        client: TestClient,
        created_applicant: dict[str, Any],
        mock_cv_parser,
        mock_webhook,
        mock_file_write,
    ) -> None:
        resp = client.post(
            _url("/upload-cv"),
            params={"person_id": created_applicant["id"]},
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        body = resp.json()
        assert "document_id" in body
        uuid.UUID(body["document_id"])

    def test_returns_415_for_non_pdf(
        self,
        client: TestClient,
        created_applicant: dict[str, Any],
    ) -> None:
        resp = client.post(
            _url("/upload-cv"),
            params={"person_id": created_applicant["id"]},
            files={"file": ("resume.docx", b"PK data", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code == 415

    def test_returns_404_when_person_not_found(
        self,
        client: TestClient,
        mock_cv_parser,
        mock_webhook,
        mock_file_write,
    ) -> None:
        resp = client.post(
            _url("/upload-cv"),
            params={"person_id": str(uuid.uuid4())},
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert resp.status_code == 404

    def test_calls_cv_parser_once(
        self,
        client: TestClient,
        created_applicant: dict[str, Any],
        mock_cv_parser,
        mock_webhook,
        mock_file_write,
    ) -> None:
        client.post(
            _url("/upload-cv"),
            params={"person_id": created_applicant["id"]},
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        mock_cv_parser.assert_awaited_once()

    def test_returns_401_without_auth_header(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            resp = client.post(
                _url("/upload-cv"),
                params={"person_id": created_applicant["id"]},
                files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
            )
            assert resp.status_code == 401
        finally:
            _restore_auth_override()


# ===========================================================================
# GET /api/v1/applicants/
# ===========================================================================


class TestListApplicants:
    def test_returns_200_with_empty_list(self, client: TestClient) -> None:
        resp = client.get(_url("/"))
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_returns_applicant_when_one_exists(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.get(_url("/"))
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["id"] == created_applicant["id"]

    def test_includes_pagination_metadata(self, client: TestClient) -> None:
        body = client.get(_url("/")).json()
        assert "page" in body
        assert "page_size" in body
        assert "total" in body

    def test_filters_by_status_archived_returns_0(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.get(_url("/"), params={"status": "archived"})
        assert resp.json()["total"] == 0

    def test_filters_by_status_active_returns_1(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.get(_url("/"), params={"status": "active"})
        assert resp.json()["total"] == 1

    def test_min_score_filter_returns_0_when_no_documents(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.get(_url("/"), params={"min_score": 80})
        assert resp.json()["total"] == 0

    def test_returns_401_without_auth(self, client: TestClient) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            assert client.get(_url("/")).status_code == 401
        finally:
            _restore_auth_override()

    def test_returns_422_when_min_score_exceeds_100(self, client: TestClient) -> None:
        assert client.get(_url("/"), params={"min_score": 101}).status_code == 422

    def test_returns_422_when_min_score_is_negative(self, client: TestClient) -> None:
        assert client.get(_url("/"), params={"min_score": -1}).status_code == 422


# ===========================================================================
# GET /api/v1/applicants/{id}
# ===========================================================================


class TestGetApplicant:
    def test_returns_200_with_correct_fields(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.get(_url(f"/{created_applicant['id']}"))
        assert resp.status_code == 200
        assert resp.json()["email"] == APPLICANT_PAYLOAD["email"]

    def test_returns_404_for_unknown_id(self, client: TestClient) -> None:
        assert client.get(_url(f"/{uuid.uuid4()}")).status_code == 404

    def test_404_detail_mentions_not_found(self, client: TestClient) -> None:
        resp = client.get(_url(f"/{uuid.uuid4()}"))
        assert "not found" in resp.json()["detail"].lower()

    def test_returns_422_for_non_uuid_id(self, client: TestClient) -> None:
        assert client.get(_url("/not-a-uuid")).status_code == 422

    def test_returns_401_without_auth(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            assert client.get(_url(f"/{created_applicant['id']}")).status_code == 401
        finally:
            _restore_auth_override()


# ===========================================================================
# PATCH /api/v1/applicants/{id}/status
# ===========================================================================


class TestUpdateStatus:
    def test_returns_200_when_status_changed(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.patch(
            _url(f"/{created_applicant['id']}/status"),
            json={"status": "archived"},
        )
        assert resp.status_code == 200

    def test_persists_new_status(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        applicant_id = created_applicant["id"]
        client.patch(_url(f"/{applicant_id}/status"), json={"status": "archived"})
        assert client.get(_url(f"/{applicant_id}")).json()["status"] == "archived"

    def test_returns_404_for_unknown_id(self, client: TestClient) -> None:
        resp = client.patch(_url(f"/{uuid.uuid4()}/status"), json={"status": "archived"})
        assert resp.status_code == 404

    def test_returns_422_for_invalid_status_value(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        resp = client.patch(
            _url(f"/{created_applicant['id']}/status"),
            json={"status": "not_valid"},
        )
        assert resp.status_code == 422

    def test_returns_401_without_auth(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            resp = client.patch(
                _url(f"/{created_applicant['id']}/status"),
                json={"status": "archived"},
            )
            assert resp.status_code == 401
        finally:
            _restore_auth_override()

    @pytest.mark.parametrize("new_status", ["active", "onboarding", "offboarding", "archived"])
    def test_accepts_all_valid_status_values(
        self, client: TestClient, new_status: str
    ) -> None:
        create_resp = client.post(
            _url("/"),
            json={**APPLICANT_PAYLOAD, "email": f"status-{new_status}@example.com"},
        )
        applicant_id = create_resp.json()["id"]
        resp = client.patch(_url(f"/{applicant_id}/status"), json={"status": new_status})
        assert resp.status_code == 200
        assert resp.json()["status"] == new_status


# ===========================================================================
# POST /api/v1/applicants/{id}/invite
# ===========================================================================


class TestSendInvite:
    def test_returns_202_when_invite_sent(
        self, client: TestClient, created_applicant: dict[str, Any], mock_webhook
    ) -> None:
        resp = client.post(_url(f"/{created_applicant['id']}/invite"))
        assert resp.status_code == 202

    def test_returns_invite_sent_status_in_body(
        self, client: TestClient, created_applicant: dict[str, Any], mock_webhook
    ) -> None:
        resp = client.post(_url(f"/{created_applicant['id']}/invite"))
        assert resp.json() == {"status": "invite_sent"}

    def test_calls_webhook_once(
        self, client: TestClient, created_applicant: dict[str, Any], mock_webhook
    ) -> None:
        client.post(_url(f"/{created_applicant['id']}/invite"))
        mock_webhook.assert_awaited_once()

    def test_webhook_payload_contains_applicant_id(
        self, client: TestClient, created_applicant: dict[str, Any], mock_webhook
    ) -> None:
        applicant_id = created_applicant["id"]
        client.post(_url(f"/{applicant_id}/invite"))
        call_args = mock_webhook.call_args
        payload: dict = call_args.args[1] if call_args.args else call_args.kwargs["payload"]
        assert payload["applicant_id"] == applicant_id

    def test_returns_404_for_unknown_id(
        self, client: TestClient, mock_webhook
    ) -> None:
        assert client.post(_url(f"/{uuid.uuid4()}/invite")).status_code == 404

    def test_returns_401_without_auth(
        self, client: TestClient, created_applicant: dict[str, Any]
    ) -> None:
        from app.api.v1.dependencies import get_current_user
        from app.main import app

        app.dependency_overrides.pop(get_current_user, None)
        try:
            assert client.post(_url(f"/{created_applicant['id']}/invite")).status_code == 401
        finally:
            _restore_auth_override()
