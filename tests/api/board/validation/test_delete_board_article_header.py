# 게시글 삭제 POST /board/article/delete API 테스트 — API_BAD_014 ~ 015

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.board.article_cleanup import BoardArticleCleanupRegistry
from tests.api.common.payload import board_article_delete_data
from tests.api.common.assertions import assert_board_article_delete_success

logger = logging.getLogger(__name__)


API_BAD_014_TC = dict(id="API_BAD_014", group="Validation - headers", title="x-elice-org-name-short header 누락", expected="경로의 org 기준으로 삭제 성공")
API_BAD_015_TC = dict(id="API_BAD_015", group="Validation - headers", title="x-elice-org-name-short header 잘못된 값", expected="경로의 org 기준으로 삭제 성공")

HEADER_CASES = [
    pytest.param(
        "API_BAD_014",
        {"include_org": False},
        "조직 헤더 누락",
        id="API_BAD_014_org_header_missing",
        marks=pytest.mark.tc(**API_BAD_014_TC),
    ),
    pytest.param(
        "API_BAD_015",
        {"org_name_short": "invalid-org"},
        "잘못된 조직 헤더 값",
        id="API_BAD_015_org_header_invalid",
        marks=pytest.mark.tc(**API_BAD_015_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, client_options, title", HEADER_CASES)
def test_delete_board_article_org_header_validation(
    api_client_factory,
    access_token: str,
    deletable_board_article_id: int,
    board_article_cleanup_registry: BoardArticleCleanupRegistry,
    tc_id: str,
    client_options: dict,
    title: str,
) -> None:
    """REST 경로의 org가 유효하면 조직 헤더와 무관하게 삭제되어야 한다."""
    client = api_client_factory(access_token=access_token, **client_options)
    data = board_article_delete_data(board_article_id=deletable_board_article_id)
    response = OrgBoardArticleApi(client).post_delete_article(data=data)

    logger.info("[%s] %s | %s", tc_id, title, response.request.url)
    assert_board_article_delete_success(response)
    board_article_cleanup_registry.mark_deleted(deletable_board_article_id)
