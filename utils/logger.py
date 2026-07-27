"""API 테스트 공통 로거.

- logger / get_logger: 프로젝트 공통 logger 객체 공유
- log_request_failure: API 실패 시 표준 형식으로 로그
- redact / SecretRedactingFilter: 콘솔·파일·Allure 로그의 민감정보 마스킹
- format_request / format_response / install_api_call_logging:
  tests/api/conftest.py의 autouse fixture에서 쓰는 전 도메인 요청/응답 자동 로깅
- log_direct_request / log_direct_response:
  ApiClient를 거치지 않는 requests 호출의 공통 로깅
  (ApiClient.request를 monkeypatch로 감싸므로 공용 utils/api_client.py는 수정하지 않고,
   테스트가 끝나면 자동 원복됩니다.)

사용 예 (tests/api/conftest.py):

    import pytest
    from utils.logger import get_logger, install_api_call_logging

    logger = get_logger(__name__)

    @pytest.fixture(autouse=True)
    def _log_api_calls(monkeypatch):
        install_api_call_logging(monkeypatch, logger)
"""

from __future__ import annotations
import logging
import re
from typing import Any


logger = logging.getLogger("api_test")


# 로그에 값이 나타나면 반드시 가려야 하는 키입니다. 대소문자와 -, _ 차이를 무시합니다.
SENSITIVE_KEYS = {
    "authorization",
    "apikey",
    "cookie",
    "setcookie",
    "accesstoken",
    "refreshtoken",
    "token",
    "password",
    "passwd",
    "pw",
    "secret",
    "webhookurl",
}
MASK = "***"
BODY_PREVIEW_LIMIT = 800


def _normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def is_sensitive_key(key: Any) -> bool:
    """키 이름이 비밀번호·토큰 등 민감정보를 의미하는지 확인합니다."""
    normalized = _normalized_key(key)
    return normalized in SENSITIVE_KEYS or normalized.endswith("token") or normalized.endswith("password")


def redact(value: Any) -> Any:
    """dict/list 내부의 민감정보 값을 재귀적으로 마스킹합니다."""
    if isinstance(value, dict):
        return {
            key: MASK if is_sensitive_key(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


_TEXT_SECRET_PATTERNS = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(
        r'''(?ix)(["']?(?:password|passwd|pw|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|cookie|secret|webhook[_-]?url)["']?\s*[:=]\s*)
        (["']?)[^,}\]\s&]+\2'''
    ),
)


def redact_text(value: Any) -> str:
    """문자열 형태의 JSON·URL·예외 메시지에 포함된 비밀값을 마스킹합니다."""
    text = str(value)
    for pattern in _TEXT_SECRET_PATTERNS:
        text = pattern.sub(lambda match: f"{match.group(1)}{MASK}", text)
    return text


class SecretRedactingFilter(logging.Filter):
    """모든 logger 출력 직전에 민감정보를 제거하는 공통 필터입니다."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.msg)
        if isinstance(record.args, dict):
            record.args = redact(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(
                redact_text(item) if isinstance(item, str) else redact(item)
                for item in record.args
            )
        return True


def install_secret_redaction() -> SecretRedactingFilter:
    """현재 등록된 root handler에 마스킹 필터를 설치합니다."""
    redacting_filter = SecretRedactingFilter()
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if not any(isinstance(item, SecretRedactingFilter) for item in handler.filters):
            handler.addFilter(redacting_filter)
    return redacting_filter


def get_logger(name: str | None = None) -> logging.Logger:
    """공통 logger를 반환합니다.

    - name 없이 호출: 프로젝트 공통 logger("api_test")를 반환 (기존 동작 유지).
    - name 지정: 해당 이름의 모듈 logger를 반환.

    handler와 formatter는 `pytest.ini`가 관리합니다. 여기서 handler를 추가하면
    pytest 로그 파일 설정과 중복 출력될 수 있으므로 logger 객체만 공유합니다.
    """
    if name is not None:
        return logging.getLogger(name)
    return logger


def log_request_failure(response: Any, context: str = "") -> None:
    """API 실패 시 요청/응답 정보를 표준 형식으로 로그에 남깁니다."""
    try:
        body = response.json()
    except ValueError:
        body = getattr(response, "text", "")

    request = getattr(response, "request", None)
    request_url = getattr(request, "url", getattr(response, "url", ""))
    request_body = getattr(request, "body", None)
    context_text = f" {context}" if context else ""

    logger.error(
        "[API 실패]%s URL=%s request_body=%s status_code=%s body=%s",
        context_text,
        redact_text(request_url),
        redact(request_body) if not isinstance(request_body, str) else redact_text(request_body),
        getattr(response, "status_code", ""),
        redact(body) if not isinstance(body, str) else redact_text(body),
    )


# =========================================================
# 요청/응답 자동 로깅 (conftest의 autouse fixture에서 사용)
# =========================================================

def format_request(method: str, base_url: str, path: str, **kwargs: Any) -> str:
    """요청 한 줄 요약: '메서드 경로  params=... body=종류'."""
    params = kwargs.get("params")
    body_kind = (
        "json" if "json" in kwargs
        else "multipart" if "files" in kwargs
        else "form" if "data" in kwargs
        else None
    )
    tail = f" body={body_kind}" if body_kind else ""
    return f"{method} {redact_text(path)}  params={redact(params)}{tail}"


def format_response(resp: Any) -> str:
    """응답 한 줄 요약: HTTP status + (REST면) _result.status/fail_code + (배열이면) 건수."""
    extra = ""
    try:
        body = resp.json()
        if isinstance(body, dict) and "_result" in body:
            result = body.get("_result") or {}
            extra = f" | _result={result.get('status')}({result.get('status_code')})"
            if body.get("fail_code"):
                extra += f" fail_code={body['fail_code']}"
        elif isinstance(body, list):
            extra = f" | 배열 {len(body)}건"
    except Exception:
        pass
    return f"status={getattr(resp, 'status_code', '?')}{extra}"


def _preview(value: Any, limit: int = BODY_PREVIEW_LIMIT) -> str:
    """긴 값은 limit까지만 보여주고 나머지는 '...(+N)'으로 요약."""
    safe_value = redact_text(value) if isinstance(value, str) else redact(value)
    text = safe_value if isinstance(safe_value, str) else repr(safe_value)
    text = " ".join(text.split())  # 개행/과다 공백 정리
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...(+{len(text) - limit})"


def _request_payload(kwargs: dict) -> Any:
    """요청 본문(payload)을 추출. multipart(files)는 필드 값만 뽑아 요약."""
    if "json" in kwargs:
        return kwargs["json"]
    if "data" in kwargs:
        return kwargs["data"]
    if "files" in kwargs:
        files = kwargs["files"]
        if isinstance(files, dict):
            return {k: (v[1] if isinstance(v, tuple) else v) for k, v in files.items()}
        if isinstance(files, (list, tuple)):
            return {name: (val[1] if isinstance(val, tuple) else val) for name, val in files}
        return files
    return None


def log_direct_request(log: logging.Logger, method: str, url: str, **kwargs: Any) -> None:
    """ApiClient를 거치지 않는 requests 호출도 같은 형식으로 기록합니다."""
    path = url.split("?", 1)[0]
    log.info("  → 요청 %s", format_request(method, "", path, **kwargs))
    payload = _request_payload(kwargs)
    if payload is not None:
        log.debug("     payload=%s", _preview(payload))


def log_direct_response(log: logging.Logger, response: Any) -> None:
    """직접 requests 호출의 응답을 공통 형식으로 기록합니다."""
    log.info("  ← 응답 %s", format_response(response))
    body_text = getattr(response, "text", "") or ""
    if body_text:
        log.debug("     body=%s", _preview(body_text))


def install_api_call_logging(monkeypatch, log: logging.Logger | None = None) -> None:
    """테스트 동안 ApiClient의 모든 요청/응답을 자동 로깅한다.

    ApiClient.request를 감싸(monkeypatch) 아래를 찍는다:
      → 요청  : 메서드·경로·파라미터·본문 종류   (INFO - 평소에도 보임)
        payload: 요청 본문 전체(잘림)              (DEBUG - --log-cli-level=DEBUG 일 때만)
      ← 응답  : status·_result·건수               (INFO - 평소에도 보임)
        body   : 응답 본문 전체(잘림)              (DEBUG - --log-cli-level=DEBUG 일 때만)
    monkeypatch라 테스트 종료 시 자동 원복된다. log 미지정 시 공통 logger를 쓴다.
    """
    from utils.api_client import ApiClient

    _log = log if log is not None else logger
    original = ApiClient.request

    def logged_request(self, method, base_url, path, **kwargs):
        _log.info("  → 요청 %s", format_request(method, base_url, path, **kwargs))
        payload = _request_payload(kwargs)
        if payload is not None:
            _log.debug("     payload=%s", _preview(payload))

        resp = original(self, method, base_url, path, **kwargs)

        _log.info("  ← 응답 %s", format_response(resp))
        body_text = getattr(resp, "text", "") or ""
        if body_text:
            _log.debug("     body=%s", _preview(body_text))
        return resp

    monkeypatch.setattr(ApiClient, "request", logged_request)
