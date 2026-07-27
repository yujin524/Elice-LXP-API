"""로그인 access_token 발급 유틸."""
from __future__ import annotations
import logging
import requests
from config.settings import AUTH_URL, API_TIMEOUT_SECONDS
from utils.error_list import (
    LOGIN_ACCESS_TOKEN_MISSING,
    LOGIN_ENV_CREDENTIALS_MISSING,
    LOGIN_FAILED,
    LOGIN_REQUEST_FAILED,
    LOGIN_RESPONSE_JSON_PARSE_FAILED,
)
from utils.logger import log_direct_request, log_direct_response, redact_text


logger = logging.getLogger(__name__)


def get_token(login_id: str, password: str) -> str:
    """로그인 API로 access_token을 발급받습니다."""
    login_url = f"{AUTH_URL}/login/pw"
    request_json = {"login_id": login_id, "password": password}
    log_direct_request(logger, "POST", login_url, json=request_json)
    try:
        response = requests.post(
            login_url,
            json=request_json,
            timeout=API_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError(LOGIN_REQUEST_FAILED.format(exc=redact_text(exc))) from exc

    log_direct_response(logger, response)

    if response.status_code != 200:
        raise RuntimeError(LOGIN_FAILED.format(status=response.status_code, body=response.text))

    try:
        response_body = response.json()
    except ValueError as exc:
        raise RuntimeError(LOGIN_RESPONSE_JSON_PARSE_FAILED.format(body=response.text)) from exc

    access_token = response_body.get("access_token") if isinstance(response_body, dict) else None
    if not access_token:
        raise RuntimeError(LOGIN_ACCESS_TOKEN_MISSING.format(body=response_body))

    return access_token


def get_access_token_from_env() -> str:
    """.env의 ELICE_ID, ELICE_PW로 로그인해서 access_token을 자동 발급받습니다.

    cmd에서 아이디/비밀번호를 직접 입력하는 대신, .env에 미리 넣어둔 값을 씁니다.
    """
    from config.settings import ELICE_ID, ELICE_PW

    if not ELICE_ID or not ELICE_PW:
        raise RuntimeError(LOGIN_ENV_CREDENTIALS_MISSING)

    return get_token(ELICE_ID, ELICE_PW)
