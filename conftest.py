"""API 테스트 전역 설정(conftest).

pytest가 자동으로 읽는 최상위 conftest입니다. 전역 hook과, 도메인(course/게시판 등)에
상관없이 공통으로 쓰는 인증/클라이언트/식별자 fixture를 관리합니다.
- 라이브 API 실행 안전장치(pytest_collection_modifyitems)
- 결과 리포트 플러그인 등록(pytest_plugins)
- 공용 fixture: 인증(access_token 등), 클라이언트(api_client 등),
  도메인 공용 식별자(classroom_id, cohort_id, student_user_id)

특정 화면에서만 쓰는 체이닝 fixture(course_id, lecture_id 등)는 각 도메인 폴더의
conftest.py에서 관리합니다. 예: tests/api/course/conftest.py
"""

from __future__ import annotations
import base64
import json
import logging
import os
from types import SimpleNamespace
import pytest
from config import settings
from tests.api.plugins.allure_metadata import apply_allure_metadata
from utils.api_client import ApiClient, response_debug_message
from utils.auth_token import get_access_token_from_env
from utils.logger import install_secret_redaction


pytest_plugins = ("tests.api.plugins.api_reporting",)
logger = logging.getLogger(__name__)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item) -> None:
    """fixture 실행 전에 비밀값 마스킹과 Allure 분류를 적용합니다."""
    install_secret_redaction()
    apply_allure_metadata(item)


def pytest_collection_modifyitems(config, items) -> None:
    """실수로 실제 API를 호출하지 않도록 기본 실행에서는 API 테스트를 skip합니다.

    실제 서버에 요청을 보내려면 실행 전에 `RUN_LIVE_API_TESTS=1`을 설정해야 합니다.
    """
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        skip_live_api = pytest.mark.skip(reason="Set RUN_LIVE_API_TESTS=1 to run live API tests.")
        for item in items:
            if "api" in item.keywords:
                item.add_marker(skip_live_api)
        return

    if settings.TEST_ENV == "prod" and not settings.ALLOW_PROD_AUTHZ_MUTATION_TESTS:
        skip_prod_sensitive = pytest.mark.skip(
            reason=(
                "운영환경 Board 권한/변경 테스트는 기본 Skip입니다. "
                "ALLOW_PROD_AUTHZ_MUTATION_TESTS=1로 명시적으로 허용할 수 있습니다."
            )
        )
        for item in items:
            if "board_authz" in item.keywords or "board_mutation" in item.keywords:
                item.add_marker(skip_prod_sensitive)


def _user_id_from_token(access_token: str) -> int | None:
    """JWT access_token에서 현재 사용자 id(_id)를 추출합니다. 실패하면 None."""
    try:
        payload_b64 = access_token.split(".")[1]
        padded_payload = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload))
    except (IndexError, ValueError, json.JSONDecodeError):
        return None

    return payload.get("_id")


def _classroom_names(classrooms: list[dict]) -> str:
    """skip 메시지에 표시할 classroom 이름 목록을 만듭니다."""
    return ", ".join(item.get("name", "<이름 없음>") for item in classrooms)


def _find_classroom_by_name(classrooms: list[dict], keyword: str) -> dict | None:
    """classroom 이름에 keyword가 포함된 항목을 찾습니다."""
    return next((item for item in classrooms if keyword in item.get("name", "")), None)


def _find_available_classroom(classrooms: list[dict]) -> dict | None:
    """현재 계정이 접근 가능한 classroom 중 설정 조건을 만족하는 항목을 찾습니다."""
    for item in classrooms:
        if settings.CLASSROOM_REQUIRE_OPENED and not item.get("opened", False):
            continue
        if settings.CLASSROOM_REQUIRE_COURSE and item.get("course_count", 0) <= 0:
            continue
        return item

    return None


# =========================================================
# 인증 / 세션
# =========================================================

@pytest.fixture(scope="session")
def requests_session():
    """모든 요청이 재사용하는 공통 requests.Session을 제공합니다."""
    requests = pytest.importorskip("requests")
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def access_token() -> str:
    """.env의 ELICE_ID/ELICE_PW로 로그인해서 access_token을 자동 발급받습니다."""
    try:
        return get_access_token_from_env()
    except RuntimeError as exc:
        pytest.fail(str(exc))


@pytest.fixture(scope="session")
def api_settings():
    """API 설정 모듈을 제공합니다.

    Postman의 Environment처럼 base_url, org, timeout 같은 공통 값을 담고 있습니다.
    """
    return settings


@pytest.fixture(scope="session")
def token_settings(api_settings, access_token: str) -> SimpleNamespace:
    """기존 테스트 호환용 설정 객체입니다.

    예전 테스트 일부가 `token_settings.ELICE_ACCESS_TOKEN` 또는
    `token_settings.CLASSROOM_ID`처럼 값을 읽고 있으므로 이름은 유지합니다.
    내부 토큰 발급 방식만 새 `auth_token.py` 흐름을 사용합니다.
    """
    settings_values = {
        name: getattr(api_settings, name)
        for name in dir(api_settings)
        if name.isupper()
    }
    settings_values["ELICE_ACCESS_TOKEN"] = access_token
    return SimpleNamespace(**settings_values)


# =========================================================
# HTTP 클라이언트
# =========================================================

@pytest.fixture(scope="session")
def api_client(requests_session, access_token: str) -> ApiClient:
    """정상 인증 토큰과 조직 header가 들어간 기본 API client입니다."""
    return ApiClient(requests_session, settings, access_token=access_token)


@pytest.fixture(scope="session")
def api_client_factory(requests_session):
    """테스트 케이스별로 header/token 상태가 다른 client를 만드는 함수입니다.

    사용 예:
    - api_client_factory(include_auth=False): Authorization header 없음
    - api_client_factory(access_token=""): Authorization 값 빈 값
    - api_client_factory(access_token="invalid-token"): 잘못된 토큰
    - api_client_factory(access_token=정상토큰, include_org=False): org header 없음
    """
    def create(
        *,
        access_token: str | None = None,
        org_name_short: str | None = None,
        include_auth: bool = True,
        include_org: bool = True,
    ) -> ApiClient:
        return ApiClient(
            requests_session,
            settings,
            access_token=access_token,
            org_name_short=org_name_short,
            include_auth=include_auth,
            include_org=include_org,
        )

    return create


# =========================================================
# 도메인 공용 식별자 (course / 게시판 등 여러 화면에서 사용)
# =========================================================

@pytest.fixture(scope="session")
def student_user_id(access_token: str) -> int:
    """JWT access_token에서 현재 사용자 id를 추출합니다."""
    user_id = _user_id_from_token(access_token)
    if user_id is None:
        pytest.skip("토큰에서 _id를 찾지 못했습니다.")

    logger.info("[준비] student_user_id 확보(JWT): %s", user_id)
    return user_id


@pytest.fixture(scope="session")
def classroom_id(api_client: ApiClient, access_token: str) -> str:
    """설정된 조회 정책에 맞는 classroom_id를 자동으로 찾습니다."""
    lookup_mode = settings.CLASSROOM_LOOKUP_MODE
    params = {"skip": 0, "count": 20}

    if lookup_mode == "available":
        user_id = _user_id_from_token(access_token)
        if user_id is None:
            pytest.skip("classroom 조회에 필요한 사용자 id를 토큰에서 찾지 못했습니다.")

        params.update(
            {
                "filter_opened_list": "true",
                "filter_name": "%%",
                "filter_member_account_id": user_id,
            }
        )

    response = api_client.get(settings.API_BASE_URL, "/classroom", params=params)
    assert response.status_code == 200, response_debug_message(response, "classroom list")

    classrooms = response.json()
    if lookup_mode == "available":
        target = _find_available_classroom(classrooms)
    elif lookup_mode == "name_keyword":
        target = _find_classroom_by_name(classrooms, settings.CLASSROOM_NAME_KEYWORD)
    else:
        pytest.skip(f"지원하지 않는 CLASSROOM_LOOKUP_MODE입니다: {lookup_mode}")

    if target is None:
        classroom_names = _classroom_names(classrooms)
        if lookup_mode == "available":
            pytest.skip(f"조건에 맞는 classroom을 찾지 못했습니다. 조회된 classroom: {classroom_names}")
        pytest.skip(
            f"'{settings.CLASSROOM_NAME_KEYWORD}' 클래스룸을 찾지 못했습니다. "
            f"조회된 classroom: {classroom_names}"
        )

    logger.info(
        "[준비] classroom_id 확보(%s): %s -> %s",
        lookup_mode,
        target["name"],
        target["id"],
    )
    return target["id"]


@pytest.fixture(scope="session")
def cohort_id(api_client: ApiClient, classroom_id: str) -> int:
    """classroom의 cohort 목록에서 기본 그룹 id를 찾습니다."""
    response = api_client.get(settings.API_BASE_URL, f"/classroom/{classroom_id}/cohort")
    assert response.status_code == 200, response_debug_message(response, "cohort list")

    cohorts = response.json()
    target = next((item for item in cohorts if item.get("is_permanent")), None)
    if target is None and cohorts:
        target = cohorts[0]
    if target is None:
        pytest.skip("이 클래스룸에 cohort가 없습니다.")

    logger.info("[준비] cohort_id 확보: %s -> %s", target["name"], target["id"])
    return target["id"]
