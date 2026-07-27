# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_006 ~ 008, 022

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.assertions import assert_board_article_edit_failed

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.board_mutation


API_BAE_006_TC = dict(id="API_BAE_006", group="Validation - title", title="title 누락", expected="검증 실패, 500 미만")
API_BAE_007_TC = dict(id="API_BAE_007", group="Validation - title", title="title 빈 문자열", expected="검증 실패, 500 미만")
API_BAE_008_TC = dict(id="API_BAE_008", group="Validation - title", title="title 최대 길이 초과", expected="검증 실패, 500 미만")
API_BAE_022_TC = dict(id="API_BAE_022", group="Validation - title", title="title 공백 1자", expected="검증 실패, 500 미만")

TITLE_INVALID_CASES = [
    pytest.param(
        "API_BAE_006",
        None,
        "title 누락",
        id="API_BAE_006_title_missing",
        marks=pytest.mark.tc(**API_BAE_006_TC),
    ),
    pytest.param(
        "API_BAE_007",
        "",
        "title 빈 문자열",
        id="API_BAE_007_title_empty",
        marks=pytest.mark.tc(**API_BAE_007_TC),
    ),
    pytest.param(
        "API_BAE_008",
        "가" * 129,
        "title 129자",
        id="API_BAE_008_title_too_long",
        marks=pytest.mark.tc(**API_BAE_008_TC),
    ),
    pytest.param(
        "API_BAE_022",
        " ",
        "title 공백 1자",
        id="API_BAE_022_title_whitespace",
        marks=pytest.mark.tc(**API_BAE_022_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, title, description", TITLE_INVALID_CASES)
def test_edit_board_article_title_validation(
    api_client,
    make_board_article_edit_payload,
    tc_id: str,
    title: str | None,
    description: str,
) -> None:
    """title 누락, 빈 문자열, 공백 문자열 또는 129자는 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(data=make_board_article_edit_payload(title=title))

    logger.info("[%s] %s", tc_id, description)
    assert_board_article_edit_failed(response)
