# 게시글 삭제 POST /board/article/delete API 테스트 — API_BAD_001, 016

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.payload import board_article_delete_data
from tests.api.common.assertions import (
    assert_board_article_delete_failed,
    assert_board_article_delete_success,
)

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.board_mutation

API_BAD_001_TC = dict(id="API_BAD_001", group="Positive", title="유효한 board_article_id로 게시글 정상 삭제", expected="HTTP 200, _result.status=ok, _result.status_code=200")
API_BAD_016_TC = dict(id="API_BAD_016", group="Validation - state", title="이미 삭제된 board_article_id 재삭제", expected="두 번째 삭제 요청은 검증 실패, 500 미만")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAD_001_TC)
def test_delete_board_article_success(
    api_client,
    deletable_board_article_id: int,
    board_article_cleanup_registry,
) -> None:
    """테스트가 생성한 게시글 ID를 삭제하면 정상 성공 응답이 반환되어야 한다."""
    data = board_article_delete_data(board_article_id=deletable_board_article_id)
    response = OrgBoardArticleApi(api_client).post_delete_article(data=data)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    logger.info("[API_BAD_001] form-data 전송")
    logger.debug("form-data=%s", data)
    assert_board_article_delete_success(response)
    board_article_cleanup_registry.mark_deleted(deletable_board_article_id)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAD_016_TC)
def test_delete_board_article_twice(
    api_client,
    deletable_board_article_id: int,
    board_article_cleanup_registry,
) -> None:
    """동일 게시글을 두 번 삭제하면 두 번째 요청은 제어 가능한 실패여야 한다."""
    data = board_article_delete_data(board_article_id=deletable_board_article_id)
    api = OrgBoardArticleApi(api_client)

    first_response = api.post_delete_article(data=data)
    assert_board_article_delete_success(first_response)
    board_article_cleanup_registry.mark_deleted(deletable_board_article_id)

    second_response = api.post_delete_article(data=data)
    assert_board_article_delete_failed(second_response)
