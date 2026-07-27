# 게시글 삭제 POST /board/article/delete API 테스트 — API_BAD_008 ~ 011

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.payload import board_article_delete_data
from tests.api.common.assertions import (
    assert_board_article_delete_failed,
)

logger = logging.getLogger(__name__)


API_BAD_008_TC = dict(id="API_BAD_008", group="Authentication", title="Authorization header 없음", expected="인증 실패, 500 미만")
API_BAD_009_TC = dict(id="API_BAD_009", group="Authentication", title="Authorization 값 없음", expected="인증 실패, 500 미만")
API_BAD_010_TC = dict(id="API_BAD_010", group="Authentication", title="Authorization 값 공백", expected="인증 실패, 500 미만")
API_BAD_011_TC = dict(id="API_BAD_011", group="Authentication", title="Authorization 임의 값", expected="인증 실패, 500 미만")

AUTH_CASES = [
    pytest.param(
        "API_BAD_008",
        {"include_auth": False},
        "Authorization header 없음",
        id="API_BAD_008_authorization_missing",
        marks=pytest.mark.tc(**API_BAD_008_TC),
    ),
    pytest.param(
        "API_BAD_009",
        {"access_token": ""},
        "Authorization 값 없음",
        id="API_BAD_009_authorization_empty",
        marks=pytest.mark.tc(**API_BAD_009_TC),
    ),
    pytest.param(
        "API_BAD_010",
        {"access_token": "  "},
        "Authorization 값 공백",
        id="API_BAD_010_authorization_blank",
        marks=pytest.mark.tc(**API_BAD_010_TC),
    ),
    pytest.param(
        "API_BAD_011",
        {"access_token": "invalid-token"},
        "Authorization 임의 값",
        id="API_BAD_011_authorization_invalid",
        marks=pytest.mark.tc(**API_BAD_011_TC),
    ),
]

@pytest.mark.api
@pytest.mark.parametrize("tc_id, client_options, title", AUTH_CASES)
def test_delete_board_article_authorization_validation(
    api_client_factory,
    tc_id: str,
    client_options: dict,
    title: str,
) -> None:
    """
    TC ID: API_BAD_008, API_BAD_009, API_BAD_010, API_BAD_011
    시나리오: Authorization header가 없거나 token이 빈 값, 공백 또는 유효하지 않은
    값이면 게시글 삭제(POST) 요청이 실패 응답으로 거부되어야 한다.
    """
    client = api_client_factory(**client_options)
    data = board_article_delete_data()
    response = OrgBoardArticleApi(client).post_delete_article(data=data)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    logger.info("[%s] %s | form-data 전송", tc_id, title)
    logger.debug("form-data=%s", data)
    assert_board_article_delete_failed(response)
