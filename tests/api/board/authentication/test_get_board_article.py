# 게시글 상세 조회 GET /board/article/get API 테스트 — API_BA_007 ~ 010

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_params
from tests.api.common.assertions import assert_board_article_get_failed

logger = logging.getLogger(__name__)

API_BA_007_TC = dict(id="API_BA_007", group="Authentication", title="Authorization header 없음", expected="HTTP 4xx 또는 REST 인증 실패")
API_BA_008_TC = dict(id="API_BA_008", group="Authentication", title="Authorization 값 없음", expected="HTTP 4xx 또는 REST 인증 실패")
API_BA_009_TC = dict(id="API_BA_009", group="Authentication", title="Authorization 값 공백", expected="HTTP 4xx 또는 REST 인증 실패")
API_BA_010_TC = dict(id="API_BA_010", group="Authentication", title="Authorization 임의 값", expected="HTTP 4xx 또는 REST 인증 실패")

AUTH_CASES = [
    pytest.param(
        "API_BA_007",
        {"include_auth": False},
        "Authorization header 없음",
        id="API_BA_007_authorization_missing",
        marks=pytest.mark.tc(**API_BA_007_TC),
    ),
    pytest.param(
        "API_BA_008",
        {"access_token": ""},
        "Authorization 값 없음",
        id="API_BA_008_authorization_empty",
        marks=pytest.mark.tc(**API_BA_008_TC),
    ),
    pytest.param(
        "API_BA_009",
        {"access_token": "  "},
        "Authorization 값 공백",
        id="API_BA_009_authorization_blank",
        marks=pytest.mark.tc(**API_BA_009_TC),
    ),
    pytest.param(
        "API_BA_010",
        {"access_token": "invalid-token"},
        "Authorization 임의 값",
        id="API_BA_010_authorization_invalid",
        marks=pytest.mark.tc(**API_BA_010_TC),
    ),
]

@pytest.mark.api
@pytest.mark.parametrize("tc_id, client_options, title", AUTH_CASES)
def test_get_board_article_authorization_validation(
    api_client_factory,
    board_article_id: int,
    tc_id: str,
    client_options,
    title: str,
) -> None:
    """
    TC ID: API_BA_007, API_BA_008, API_BA_009, API_BA_010
    시나리오: Authorization header가 없거나 token이 빈 값, 공백 또는 유효하지 않은
    값이면 게시글 상세 조회(GET) 요청이 인증 실패로 거부되어야 한다.
    """
    client = api_client_factory(**client_options)
    response = OrgBoardArticleApi(client).get_article(params=board_article_params(board_article_id=board_article_id))

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    logger.info("[%s] %s", tc_id, title)
    assert_board_article_get_failed(response)
