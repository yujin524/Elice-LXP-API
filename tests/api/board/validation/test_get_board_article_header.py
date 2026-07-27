# 게시글 상세 조회 GET /board/article/get API 테스트 — API_BA_014 ~ 015

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_params
from tests.api.common.assertions import assert_board_article

logger = logging.getLogger(__name__)


API_BA_014_TC = dict(id="API_BA_014", group="Validation - headers", title="x-elice-org-name-short header 누락", expected="경로의 org 기준으로 200 정상 조회")
API_BA_015_TC = dict(id="API_BA_015", group="Validation - headers", title="x-elice-org-name-short header 잘못된 값", expected="경로의 org 기준으로 200 정상 조회")

HEADER_CASES = [
    pytest.param(
        "API_BA_014",
        {"include_org": False},
        "조직 헤더 누락",
        id="API_BA_014_org_header_missing",
        marks=pytest.mark.tc(**API_BA_014_TC),
    ),
    pytest.param(
        "API_BA_015",
        {"org_name_short": "invalid-org"},
        "잘못된 조직 헤더 값",
        id="API_BA_015_org_header_invalid",
        marks=pytest.mark.tc(**API_BA_015_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, client_options, title", HEADER_CASES)
def test_get_board_article_org_header_validation(
    api_client_factory,
    access_token: str,
    board_article_id: int,
    tc_id: str,
    client_options: dict,
    title: str,
) -> None:
    """REST 경로의 org가 유효하면 조직 헤더와 무관하게 같은 게시글을 조회해야 한다."""
    client = api_client_factory(access_token=access_token, **client_options)
    response = OrgBoardArticleApi(client).get_article(
        params=board_article_params(board_article_id=board_article_id),
    )

    logger.info("[%s] %s | %s", tc_id, title, response.request.url)
    assert_board_article(response, board_article_id)
