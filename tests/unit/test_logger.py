"""공통 Logger의 민감정보 보호와 요약 동작을 검증합니다."""

from __future__ import annotations

import logging

from utils.logger import SecretRedactingFilter, redact, redact_text


def test_redact_masks_nested_secret_values() -> None:
    """중첩된 dict/list에 있는 비밀번호와 토큰이 모두 마스킹되는지 확인합니다."""
    source = {
        "login_id": "learner@example.com",
        "password": "real-password",
        "nested": [{"access_token": "real-token"}],
    }

    result = redact(source)

    assert result == {
        "login_id": "learner@example.com",
        "password": "***",
        "nested": [{"access_token": "***"}],
    }, f"민감정보 마스킹 결과가 예상과 다릅니다. 예상: 비밀값 ***, 실제: {result}"


def test_redact_text_masks_bearer_and_password() -> None:
    """문자열 로그의 Bearer token과 password 값이 노출되지 않는지 확인합니다."""
    result = redact_text("Authorization: Bearer real-token password=real-password")

    assert "real-token" not in result, f"Bearer token이 로그에 남았습니다. 실제: {result}"
    assert "real-password" not in result, f"password가 로그에 남았습니다. 실제: {result}"


def test_logging_filter_masks_message_arguments() -> None:
    """logger의 치환 인자로 전달된 dict도 출력 전에 마스킹되는지 확인합니다."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="payload=%s",
        args=({"password": "real-password"},),
        exc_info=None,
    )

    SecretRedactingFilter().filter(record)
    message = record.getMessage()

    assert "real-password" not in message, f"필터 적용 후 password가 남았습니다. 실제: {message}"
    assert "***" in message, f"마스킹 표시가 없습니다. 예상: ***, 실제: {message}"
