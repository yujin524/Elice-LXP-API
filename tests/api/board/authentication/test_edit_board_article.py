# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_017 ~ 020

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.assertions import assert_board_article_edit_failed

logger = logging.getLogger(__name__)


API_BAE_017_TC = dict(id="API_BAE_017", group="Authentication", title="Authorization header 없음", expected="인증 실패, 500 미만")
API_BAE_018_TC = dict(id="API_BAE_018", group="Authentication", title="Authorization 값 없음", expected="인증 실패, 500 미만")
API_BAE_019_TC = dict(id="API_BAE_019", group="Authentication", title="Authorization 값 공백", expected="인증 실패, 500 미만")
API_BAE_020_TC = dict(id="API_BAE_020", group="Authentication", title="Authorization 임의 값", expected="인증 실패, 500 미만")

AUTH_CASES = [
    pytest.param(
        "API_BAE_017",
        {"include_auth": False},
        "Authorization header 없음",
        id="API_BAE_017_authorization_missing",
        marks=pytest.mark.tc(**API_BAE_017_TC),
    ),
    pytest.param(
        "API_BAE_018",
        {"access_token": ""},
        "Authorization 값 없음",
        id="API_BAE_018_authorization_empty",
        marks=pytest.mark.tc(**API_BAE_018_TC),
    ),
    pytest.param(
        "API_BAE_019",
        {"access_token": "  "},
        "Authorization 값 공백",
        id="API_BAE_019_authorization_blank",
        marks=pytest.mark.tc(**API_BAE_019_TC),
    ),
    pytest.param(
        "API_BAE_020",
        {"access_token": "invalid-token"},
        "Authorization 임의 값",
        id="API_BAE_020_authorization_invalid",
        marks=pytest.mark.tc(**API_BAE_020_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, client_options, description", AUTH_CASES)
def test_edit_board_article_authorization_validation(
    api_client_factory,
    make_board_article_edit_payload,
    tc_id: str,
    client_options: dict,
    description: str,
) -> None:
    """
    TC ID: API_BAE_017, API_BAE_018, API_BAE_019, API_BAE_020
    시나리오: Authorization header가 없거나 token이 빈 값, 공백 또는 유효하지 않은
    값이면 게시글 생성·수정(POST) 요청이 실패 응답으로 거부되어야 한다.
    """
    client = api_client_factory(**client_options)
    response = OrgBoardArticleApi(client).post_edit_article(data=make_board_article_edit_payload())

    logger.info("[%s] %s", tc_id, description)
    assert_board_article_edit_failed(response)
