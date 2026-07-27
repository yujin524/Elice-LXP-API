# 게시판 게시글 목록·작성·조회·수정·삭제 시나리오 API 테스트 — API_SC_001

from __future__ import annotations
import json
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_list_params, board_article_params
from tests.api.common.payload import board_article_delete_data, board_article_edit_data
from tests.api.common.assertions import (
    assert_article_list,
    assert_board_article,
    assert_board_article_delete_success,
    assert_board_article_edit_success,
)
from tests.api.board.article_cleanup import build_automation_article_title

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.board_mutation

API_SC_001_TC = dict(id="API_SC_001", group="Scenario - Positive", title="게시글 목록·읽기·일반/비밀 작성·수정·삭제 정상 흐름", expected="각 API가 성공하고 테스트가 생성한 게시글의 작성·수정·삭제가 완료됨")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_SC_001_TC)
def test_board_article_happy_path(
    api_client,
    classroom_id: str,
    board_id: int,
    board_article_cleanup_registry,
) -> None:
    """게시판의 주요 정상 기능을 한 사용자 흐름으로 검증합니다."""
    api = OrgBoardArticleApi(api_client)

    logger.info("[API_SC_001][1/6] 전체 게시글 조회")
    list_response = get_article_list(
        api_client,
        classroom_id=classroom_id,
        params=board_article_list_params(count=10),
    )
    assert_article_list(list_response, classroom_id, max_count=10)

    logger.info("[API_SC_001][2/6] 일반 게시글 쓰기")
    normal_title = build_automation_article_title("API_SC_001") + "[normal]"
    normal_content = "<p>시나리오 일반 게시글 내용</p>"
    normal_payload = board_article_edit_data(
        title=normal_title,
        content=normal_content,
        is_secret="false",
        classroom_id=classroom_id,
        board_id=board_id,
    )
    normal_id = assert_board_article_edit_success(
        api.post_edit_article(data=normal_payload),
    )
    board_article_cleanup_registry.track(
        normal_id,
        api_client,
        tc_id="API_SC_001",
        owner_role="default",
    )

    logger.info("[API_SC_001][3/6] 작성한 게시글 읽기: %s", normal_id)
    read_response = api.get_article(
        params=board_article_params(board_article_id=normal_id),
    )
    read_body = assert_board_article(read_response, normal_id)
    serialized_read_body = json.dumps(read_body, ensure_ascii=False)
    assert normal_title in serialized_read_body
    assert normal_content in serialized_read_body

    logger.info("[API_SC_001][4/6] 비밀 게시글 쓰기")
    secret_payload = board_article_edit_data(
        title=build_automation_article_title("API_SC_001") + "[secret]",
        content="<p>시나리오 비밀 게시글 내용</p>",
        is_secret="true",
        classroom_id=classroom_id,
        board_id=board_id,
    )
    secret_id = assert_board_article_edit_success(
        api.post_edit_article(data=secret_payload),
    )
    board_article_cleanup_registry.track(
        secret_id,
        api_client,
        tc_id="API_SC_001",
        owner_role="default",
    )

    logger.info("[API_SC_001][5/6] 본인 게시글 수정하기: %s", normal_id)
    updated_title = build_automation_article_title("API_SC_001") + "[updated]"
    updated_content = "<p>수정된 시나리오 게시글 내용</p>"
    update_payload = board_article_edit_data(
        board_article_id=normal_id,
        title=updated_title,
        content=updated_content,
        is_secret="false",
        classroom_id=classroom_id,
        board_id=board_id,
    )
    assert assert_board_article_edit_success(
        api.post_edit_article(data=update_payload),
    ) == normal_id

    updated_response = api.get_article(
        params=board_article_params(board_article_id=normal_id),
    )
    updated_body = assert_board_article(updated_response, normal_id)
    serialized_updated_body = json.dumps(updated_body, ensure_ascii=False)
    assert updated_title in serialized_updated_body
    assert updated_content in serialized_updated_body

    logger.info("[API_SC_001][6/6] 본인 게시글 삭제하기: %s", normal_id)
    delete_response = api.post_delete_article(
        data=board_article_delete_data(board_article_id=normal_id),
    )
    assert_board_article_delete_success(delete_response)
    board_article_cleanup_registry.mark_deleted(normal_id)
