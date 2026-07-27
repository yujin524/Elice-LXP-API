"""board 도메인 공통 fixture."""

from __future__ import annotations
import logging
from typing import Any
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from config import settings
from tests.api.common.params import board_article_list_params
from tests.api.common.payload import board_article_edit_data
from tests.api.common.assertions import (
    assert_article_list,
    assert_board_article_edit_success,
)
from tests.api.board.article_cleanup import (
    BoardArticleCleanupRegistry,
    build_automation_article_title,
)
from utils.api_client import ApiClient
from utils.auth_token import get_token

logger = logging.getLogger(__name__)


def _require_authz_credentials(
    *,
    role_name: str,
    login_id: str,
    password: str,
) -> tuple[str, str]:
    """역할 계정이 준비되지 않았으면 그 계정이 필요한 테스트만 Skip합니다."""
    missing = []
    if not login_id:
        missing.append(f"{role_name}_ID")
    if not password:
        missing.append(f"{role_name}_PW")
    if missing:
        pytest.skip("권한 테스트 계정이 준비되지 않았습니다: " + ", ".join(missing))
    return login_id, password


def _get_authz_access_token(*, role_label: str, login_id: str, password: str) -> str:
    """설정된 권한 계정의 로그인 실패는 잘못된 설정이므로 Fail로 보고합니다."""
    try:
        return get_token(login_id, password)
    except RuntimeError as exc:
        pytest.fail(f"{role_label} 권한 테스트 계정 로그인 실패: {exc}")


def fetch_board_articles(api_client, classroom_id: str, *, count: int = 10) -> list[dict[str, Any]]:
    """게시글 목록을 조회하고 공통 검증을 적용해 반환합니다."""
    response = get_article_list(
        api_client,
        classroom_id=classroom_id,
        params=board_article_list_params(count=count),
    )
    return assert_article_list(response, classroom_id, max_count=count)


def build_board_article_payload(
    classroom_id: str,
    board_id: int,
    *,
    tc_id: str = "UNASSIGNED",
    **overrides: Any,
) -> dict[str, Any]:
    """게시글 생성·수정에 사용할 기본 payload를 생성합니다."""
    data = board_article_edit_data(
        title=build_automation_article_title(tc_id),
        classroom_id=classroom_id,
        board_id=board_id,
    )
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return data


def get_existing_article_id(api_client, classroom_id: str, *, count: int = 1) -> int:
    """게시글 목록에서 첫 게시글의 article_id를 반환합니다."""
    articles = fetch_board_articles(api_client, classroom_id, count=count)
    if not articles:
        pytest.skip("board_article_id로 사용할 게시글을 찾지 못했습니다.")
    return articles[0]["id"]


def get_existing_board_id(api_client, classroom_id: str, *, count: int = 10) -> int:
    """게시글 목록에서 생성/삭제 검증에 사용할 board_id를 찾습니다."""
    articles = fetch_board_articles(api_client, classroom_id, count=count)
    target = next((item for item in articles if isinstance(item.get("board_id"), int)), None)
    if target is None:
        pytest.skip("board_id 기반 검증에 사용할 게시글이 없습니다.")
    return target["board_id"]


def create_board_article_and_return_id(
    api_client,
    classroom_id: str,
    board_id: int,
    **overrides: Any,
) -> int:
    """게시글을 생성하고 생성된 board_article_id를 반환합니다."""
    data = build_board_article_payload(classroom_id, board_id, **overrides)
    response = OrgBoardArticleApi(api_client).post_edit_article(data=data)
    return assert_board_article_edit_success(response)


def _authz_token(*, role_name: str, role_label: str, login_id: str, password: str) -> str:
    login_id, password = _require_authz_credentials(
        role_name=role_name,
        login_id=login_id,
        password=password,
    )
    return _get_authz_access_token(
        role_label=role_label,
        login_id=login_id,
        password=password,
    )


@pytest.fixture(scope="session")
def authz_classroom_id() -> str:
    """권한 테스트 전용 classroom ID를 제공합니다."""
    if not settings.AUTHZ_CLASSROOM_ID:
        pytest.skip("권한 테스트 대상이 준비되지 않았습니다: AUTHZ_CLASSROOM_ID")
    return settings.AUTHZ_CLASSROOM_ID


@pytest.fixture(scope="session")
def educator_a_client(requests_session) -> ApiClient:
    token = _authz_token(
        role_name="DEV_EDUCATOR_A", role_label="교육자 A",
        login_id=settings.DEV_EDUCATOR_A_ID, password=settings.DEV_EDUCATOR_A_PW,
    )
    return ApiClient(requests_session, settings, access_token=token)


@pytest.fixture(scope="session")
def educator_b_client(requests_session) -> ApiClient:
    token = _authz_token(
        role_name="DEV_EDUCATOR_B", role_label="교육자 B",
        login_id=settings.DEV_EDUCATOR_B_ID, password=settings.DEV_EDUCATOR_B_PW,
    )
    return ApiClient(requests_session, settings, access_token=token)


@pytest.fixture(scope="session")
def learner_a_client(requests_session) -> ApiClient:
    token = _authz_token(
        role_name="DEV_LEARNER_A", role_label="학습자 A",
        login_id=settings.DEV_LEARNER_A_ID, password=settings.DEV_LEARNER_A_PW,
    )
    return ApiClient(requests_session, settings, access_token=token)


@pytest.fixture(scope="session")
def learner_b_client(requests_session) -> ApiClient:
    token = _authz_token(
        role_name="DEV_LEARNER_B", role_label="학습자 B",
        login_id=settings.DEV_LEARNER_B_ID, password=settings.DEV_LEARNER_B_PW,
    )
    return ApiClient(requests_session, settings, access_token=token)


@pytest.fixture(scope="session")
def outsider_client(requests_session) -> ApiClient:
    token = _authz_token(
        role_name="DEV_OUTSIDER", role_label="비소속 사용자",
        login_id=settings.DEV_OUTSIDER_ID, password=settings.DEV_OUTSIDER_PW,
    )
    return ApiClient(requests_session, settings, access_token=token)


@pytest.fixture(scope="session")
def authz_board_id(educator_a_client, authz_classroom_id: str) -> int:
    """권한 테스트 classroom에서 게시글 작성에 사용할 board ID를 찾습니다."""
    return get_existing_board_id(educator_a_client, authz_classroom_id)


@pytest.fixture
def make_board_article_edit_payload(classroom_id: str, board_id: int):
    """게시글 생성·수정에 사용할 payload 생성 fixture를 제공합니다."""

    def make(**overrides: Any):
        payload_options = {
            "classroom_id": classroom_id,
            "board_id": board_id,
        }
        payload_options.update(overrides)
        return build_board_article_payload(**payload_options)

    return make


@pytest.fixture(scope="session")
def board_id(api_client, classroom_id: str) -> int:
    """게시글 목록 응답에서 생성/삭제 검증에 사용할 유효한 board_id를 찾습니다."""
    return get_existing_board_id(api_client, classroom_id)


@pytest.fixture(scope="session")
def board_article_id(api_client, classroom_id: str) -> int:
    """게시글 상세 조회에 사용할 board_article_id를 게시글 목록에서 가져옵니다."""
    article_id = get_existing_article_id(api_client, classroom_id, count=1)
    logger.info("[준비] board_article_id 확보: %s", article_id)
    return article_id

@pytest.fixture
def deletable_board_article_id(
    api_client,
    classroom_id: str,
    board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> int:
    """정상 삭제 테스트가 직접 생성한 게시글 ID를 제공합니다."""
    article_id = create_board_article_and_return_id(
        api_client,
        classroom_id,
        board_id,
        tc_id="API_BAD_DELETE_FIXTURE",
    )
    return board_article_cleanup_registry.track(
        article_id,
        api_client,
        tc_id="API_BAD_DELETE_FIXTURE",
        owner_role="default",
    )


@pytest.fixture
def board_article_cleanup_registry():
    """Board 테스트별 생성 게시글을 작성자 권한으로 정리합니다."""
    registry = BoardArticleCleanupRegistry()
    yield registry
    registry.cleanup()
