# Board 권한 테스트 계정 준비 정책 단위 테스트 — API_AUTHZ_B_001 ~ 009

from __future__ import annotations
import pytest
from tests.api.board import conftest as board_conftest


def test_missing_authz_credentials_skips_only_dependent_test():
    with pytest.raises(pytest.skip.Exception, match="DEV_LEARNER_A_ID, DEV_LEARNER_A_PW"):
        board_conftest._require_authz_credentials(
            role_name="DEV_LEARNER_A",
            login_id="",
            password="",
        )


def test_complete_authz_credentials_are_returned():
    credentials = board_conftest._require_authz_credentials(
        role_name="DEV_LEARNER_A",
        login_id="learner@example.com",
        password="secret",
    )

    assert credentials == ("learner@example.com", "secret")


def test_authz_classroom_fixture_skips_when_target_is_missing(monkeypatch):
    monkeypatch.setattr(board_conftest.settings, "AUTHZ_CLASSROOM_ID", "")
    with pytest.raises(pytest.skip.Exception, match="AUTHZ_CLASSROOM_ID"):
        board_conftest.authz_classroom_id.__wrapped__()


def test_configured_authz_account_login_failure_is_not_hidden_as_skip(monkeypatch):
    def fail_login(login_id: str, password: str) -> str:
        raise RuntimeError("invalid credentials")

    monkeypatch.setattr(board_conftest, "get_token", fail_login)

    with pytest.raises(pytest.fail.Exception, match="학습자 권한 테스트 계정 로그인 실패"):
        board_conftest._get_authz_access_token(
            role_label="학습자",
            login_id="learner@example.com",
            password="wrong",
        )


def test_configured_authz_account_returns_token(monkeypatch):
    monkeypatch.setattr(board_conftest, "get_token", lambda login_id, password: "access-token")

    token = board_conftest._get_authz_access_token(
        role_label="타 교육자",
        login_id="educator@example.com",
        password="secret",
    )

    assert token == "access-token"
