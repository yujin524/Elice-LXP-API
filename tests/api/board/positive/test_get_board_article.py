# 게시글 상세 조회 GET /board/article/get API 테스트 — API_BA_001, 016

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_params
from tests.api.common.assertions import assert_board_article

logger = logging.getLogger(__name__)

API_BA_001_TC = dict(id="API_BA_001", group="Positive", title="게시글 상세 정상 조회", expected="200, JSON 객체, 게시글 필드 존재")
API_BA_016_TC = dict(id="API_BA_016", group="Positive", title="게시글 상세 응답 메타 필드 검증", expected="작성자, 비밀글 여부, 생성일 필드 존재")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BA_001_TC)
def test_get_board_article_success(api_client, board_article_id: int) -> None:
    """
    TC ID: API_BA_001
    시나리오: 유효한 board_article_id로 게시글 상세 조회(GET) API를 호출하면
    200 상태 코드와 게시글 상세 정보가 반환되어야 한다.
    """
    response = OrgBoardArticleApi(api_client).get_article(params=board_article_params(board_article_id=board_article_id))

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_board_article(response, board_article_id)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BA_016_TC)
def test_get_board_article_response_metadata(api_client, board_article_id: int) -> None:
    """정상 상세 응답에는 작성자·비밀글 여부·생성일 메타 정보가 있어야 한다."""
    response = OrgBoardArticleApi(api_client).get_article(
        params=board_article_params(board_article_id=board_article_id),
    )
    body = assert_board_article(response, board_article_id)
    article = body.get("article") or body.get("board_article") or body

    assert any(key in article for key in {"user", "author", "account"})
    assert "is_secret" in article
    assert any(key in article for key in {"created_datetime", "created_at", "created_date"})
