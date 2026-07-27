# 게시글 역할·소유권 권한 경계 API 테스트 — API_AUTHZ_B_001 ~ 009

from __future__ import annotations
import json
from typing import Any
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.board.article_cleanup import (
    BoardArticleCleanupRegistry,
    build_automation_article_title,
)
from tests.api.common.assertions import (
    assert_board_article,
    assert_board_article_delete_failed,
    assert_board_article_delete_success,
    assert_board_article_edit_failed,
    assert_board_article_edit_success,
    assert_board_article_get_failed,
    assert_board_article_values_not_exposed,
    extract_board_article,
)
from tests.api.common.params import board_article_params
from tests.api.common.payload import board_article_delete_data, board_article_edit_data


API_AUTHZ_B_001_TC = dict(id="API_AUTHZ_B_001", group="Authorization", title="학습자 본인 글 작성·수정·삭제", expected="학습자 본인 글 작성·수정·삭제 성공")
API_AUTHZ_B_002_TC = dict(id="API_AUTHZ_B_002", group="Authorization", title="학습자 타인 일반 글 조회", expected="타 학습자의 일반 글 조회 성공")
API_AUTHZ_B_003_TC = dict(id="API_AUTHZ_B_003", group="Authorization", title="학습자 타인 비밀글 조회 거부", expected="권한 실패")
API_AUTHZ_B_004_TC = dict(id="API_AUTHZ_B_004", group="Authorization", title="학습자 타인 일반 글 수정 거부", expected="권한 실패 및 원문 유지")
API_AUTHZ_B_005_TC = dict(id="API_AUTHZ_B_005", group="Authorization", title="학습자 타인 일반 글 삭제 거부", expected="권한 실패 및 게시글 유지")
API_AUTHZ_B_006_TC = dict(id="API_AUTHZ_B_006", group="Authorization", title="교육자 타인 일반글 조회", expected="일반글 조회 성공")
API_AUTHZ_B_007_TC = dict(id="API_AUTHZ_B_007", group="Authorization", title="교육자 타인 비밀글 조회", expected="비밀글 조회 성공")
API_AUTHZ_B_008_TC = dict(id="API_AUTHZ_B_008", group="Authorization", title="교육자 타인 글 수정", expected="수정 성공")
API_AUTHZ_B_009_TC = dict(id="API_AUTHZ_B_009", group="Authorization", title="교육자 타인 글 삭제", expected="삭제 성공")

EDUCATOR_READ_CASES = [
    pytest.param(
        "API_AUTHZ_B_006",
        False,
        id="API_AUTHZ_B_006_public",
        marks=pytest.mark.tc(**API_AUTHZ_B_006_TC),
    ),
    pytest.param(
        "API_AUTHZ_B_007",
        True,
        id="API_AUTHZ_B_007_secret",
        marks=pytest.mark.tc(**API_AUTHZ_B_007_TC),
    ),
]


def create_authz_board_article(
    owner_client,
    cleanup_registry: BoardArticleCleanupRegistry,
    classroom_id: str,
    board_id: int,
    tc_id: str,
    *,
    owner_role: str,
    is_secret: bool = False,
) -> tuple[int, dict[str, Any]]:
    """권한 검증용 게시글을 생성하고 작성자 기준 cleanup 대상으로 등록합니다."""
    payload = board_article_edit_data(
        title=build_automation_article_title(tc_id),
        content=f"<p>{tc_id} 권한 테스트 원문</p>",
        is_secret=str(is_secret).lower(),
        classroom_id=classroom_id,
        board_id=board_id,
    )
    response = OrgBoardArticleApi(owner_client).post_edit_article(data=payload)
    board_article_id = assert_board_article_edit_success(response)
    cleanup_registry.track(
        board_article_id,
        owner_client,
        tc_id=tc_id,
        owner_role=owner_role,
    )
    return board_article_id, payload


def get_board_article(client, board_article_id: int):
    """지정한 client로 게시글 상세를 조회합니다."""
    return OrgBoardArticleApi(client).get_article(
        params=board_article_params(board_article_id=board_article_id),
    )


def is_rest_success(response) -> bool:
    """예상 밖 성공으로 삭제된 데이터를 cleanup 대상에서 제외할 때 사용합니다."""
    if response.status_code != 200:
        return False
    return response.json().get("_result", {}).get("status") == "ok"


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.tc(**API_AUTHZ_B_001_TC)
def test_learner_can_create_edit_delete_own_article(
    learner_a_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_001
    시나리오: 학습자 A가 일반 게시글을 작성한 뒤 같은 계정으로 수정·삭제하면
    게시글 작성, 수정 내용 조회, 삭제가 모두 성공해야 한다.
    """
    board_article_id, original_payload = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_001",
        owner_role="learner_a",
    )
    updated_title = build_automation_article_title("API_AUTHZ_B_001") + "[updated]"
    update_payload = {
        **original_payload,
        "board_article_id": board_article_id,
        "title": updated_title,
    }
    update_response = OrgBoardArticleApi(learner_a_client).post_edit_article(
        data=update_payload,
    )
    assert assert_board_article_edit_success(update_response) == board_article_id

    detail_body = assert_board_article(
        get_board_article(learner_a_client, board_article_id),
        board_article_id,
    )
    assert updated_title in json.dumps(detail_body, ensure_ascii=False)

    delete_response = OrgBoardArticleApi(learner_a_client).post_delete_article(
        data=board_article_delete_data(board_article_id=board_article_id),
    )
    assert_board_article_delete_success(delete_response)
    board_article_cleanup_registry.mark_deleted(board_article_id)


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.tc(**API_AUTHZ_B_002_TC)
def test_learner_can_read_other_public_article(
    learner_a_client,
    learner_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_002
    시나리오: 학습자 A가 작성한 일반 게시글을 학습자 B가 상세 조회하면
    정상 응답과 동일한 board_article_id가 반환되어야 한다.
    """
    board_article_id, original_payload = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_002",
        owner_role="learner_a",
    )
    response = get_board_article(learner_b_client, board_article_id)
    assert_board_article(response, board_article_id)


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.bug_candidate
@pytest.mark.xfail(reason="학습자가 타 학습자의 비밀글 본문을 조회할 수 있음.")
@pytest.mark.tc(**API_AUTHZ_B_003_TC)
def test_learner_cannot_read_other_secret_article(
    learner_a_client,
    learner_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_003
    시나리오: 학습자 A가 작성한 비밀 게시글을 학습자 B가 상세 조회하면
    HTTP 또는 REST body 기반 권한 실패 응답이 반환되어야 한다.
    """
    board_article_id, original_payload = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_003",
        owner_role="learner_a",
        is_secret=True,
    )
    response = get_board_article(learner_b_client, board_article_id)
    assert_board_article_get_failed(response)
    assert_board_article_values_not_exposed(
        response,
        original_payload["title"],
        original_payload["content"],
    )


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.tc(**API_AUTHZ_B_004_TC)
def test_learner_cannot_edit_other_public_article(
    learner_a_client,
    learner_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_004
    시나리오: 학습자 A가 작성한 일반 게시글을 학습자 B가 수정하면
    권한 실패 응답이 반환되고 작성 당시 제목이 유지되어야 한다.
    """
    board_article_id, original_payload = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_004",
        owner_role="learner_a",
    )
    update_payload = {
        **original_payload,
        "board_article_id": board_article_id,
        "title": "권한 없는 수정",
    }
    update_response = OrgBoardArticleApi(learner_b_client).post_edit_article(
        data=update_payload,
    )
    assert_board_article_edit_failed(update_response)

    detail_body = assert_board_article(
        get_board_article(learner_a_client, board_article_id),
        board_article_id,
    )
    article = extract_board_article(detail_body)
    assert article["id"] == board_article_id
    assert article["title"] == original_payload["title"]
    assert article["content"] == original_payload["content"]


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.bug_candidate
@pytest.mark.xfail(reason="학습자가 타 학습자의 일반 게시글을 삭제할 수 있음.")
@pytest.mark.tc(**API_AUTHZ_B_005_TC)
def test_learner_cannot_delete_other_public_article(
    learner_a_client,
    learner_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_005
    시나리오: 학습자 A가 작성한 일반 게시글을 학습자 B가 삭제하면
    권한 실패 응답이 반환되고 작성자 계정으로 계속 조회할 수 있어야 한다.
    """
    board_article_id, _ = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_005",
        owner_role="learner_a",
    )
    delete_response = OrgBoardArticleApi(learner_b_client).post_delete_article(
        data=board_article_delete_data(board_article_id=board_article_id),
    )
    if is_rest_success(delete_response):
        board_article_cleanup_registry.mark_deleted(board_article_id)
    assert_board_article_delete_failed(delete_response)

    detail_response = get_board_article(learner_a_client, board_article_id)
    assert_board_article(detail_response, board_article_id)


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.parametrize("tc_id, is_secret", EDUCATOR_READ_CASES)
def test_educator_can_read_other_public_and_secret_article(
    tc_id: str,
    is_secret: bool,
    learner_a_client,
    educator_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_006, API_AUTHZ_B_007
    시나리오: 학습자 A가 작성한 일반글 또는 비밀글을 교육자 B가 상세 조회하면
    게시글 공개 여부와 관계없이 정상 응답이 반환되어야 한다.
    """
    board_article_id, _ = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        tc_id,
        owner_role="learner_a",
        is_secret=is_secret,
    )
    response = get_board_article(educator_b_client, board_article_id)
    assert_board_article(response, board_article_id)


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.bug_candidate
@pytest.mark.xfail(reason="교육자가 타 학습자의 게시글을 수정하면 resource_not_found가 반환됨.")
@pytest.mark.tc(**API_AUTHZ_B_008_TC)
def test_educator_can_edit_other_article(
    learner_a_client,
    educator_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_008
    시나리오: 학습자 A가 작성한 일반 게시글을 교육자 B가 수정하면
    동일한 board_article_id로 수정 성공 응답이 반환되어야 한다.
    """
    board_article_id, original_payload = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_008",
        owner_role="learner_a",
    )
    update_payload = {
        **original_payload,
        "board_article_id": board_article_id,
        "title": "교육자 권한 수정",
    }
    update_response = OrgBoardArticleApi(educator_b_client).post_edit_article(
        data=update_payload,
    )
    assert assert_board_article_edit_success(update_response) == board_article_id


@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.board_authz
@pytest.mark.board_mutation
@pytest.mark.tc(**API_AUTHZ_B_009_TC)
def test_educator_can_delete_other_article(
    learner_a_client,
    educator_b_client,
    authz_classroom_id: str,
    authz_board_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
) -> None:
    """
    TC ID: API_AUTHZ_B_009
    시나리오: 학습자 A가 작성한 일반 게시글을 교육자 B가 삭제하면
    REST 성공 응답이 반환되고 cleanup 중복 삭제가 발생하지 않아야 한다.
    """
    board_article_id, _ = create_authz_board_article(
        learner_a_client,
        board_article_cleanup_registry,
        authz_classroom_id,
        authz_board_id,
        "API_AUTHZ_B_009",
        owner_role="learner_a",
    )
    delete_response = OrgBoardArticleApi(educator_b_client).post_delete_article(
        data=board_article_delete_data(board_article_id=board_article_id),
    )
    if is_rest_success(delete_response):
        board_article_cleanup_registry.mark_deleted(board_article_id)
    assert_board_article_delete_success(delete_response)
