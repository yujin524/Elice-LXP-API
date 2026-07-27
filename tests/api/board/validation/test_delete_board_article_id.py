# 게시글 삭제 POST /board/article/delete API 테스트 — API_BAD_002 ~ 007, 012 ~ 013

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.payload import board_article_delete_data
from tests.api.common.assertions import (
    assert_board_article_delete_failed,
)

logger = logging.getLogger(__name__)


API_BAD_002_TC = dict(id="API_BAD_002", group="Validation - board_article_id", title="board_article_id 누락", expected="검증 실패, 500 미만")
API_BAD_003_TC = dict(id="API_BAD_003", group="Validation - board_article_id", title="board_article_id 빈 문자열", expected="검증 실패, 500 미만")
API_BAD_004_TC = dict(id="API_BAD_004", group="Validation - board_article_id", title="board_article_id 문자열", expected="검증 실패, 500 미만")
API_BAD_005_TC = dict(id="API_BAD_005", group="Validation - board_article_id", title="board_article_id 0", expected="검증 실패, 500 미만")
API_BAD_006_TC = dict(id="API_BAD_006", group="Validation - board_article_id", title="board_article_id 음수", expected="검증 실패, 500 미만")
API_BAD_007_TC = dict(id="API_BAD_007", group="Validation - board_article_id", title="존재하지 않는 board_article_id", expected="검증 실패, 500 미만")
API_BAD_012_TC = dict(id="API_BAD_012", group="Validation - board_article_id", title="board_article_id 실수형 문자열", expected="검증 실패, 500 미만")
API_BAD_013_TC = dict(id="API_BAD_013", group="Validation - board_article_id", title="board_article_id 매우 큰 정수", expected="검증 실패, 500 미만")

BOARD_ARTICLE_ID_CASES = [
    pytest.param(
        "API_BAD_002",
        board_article_delete_data(board_article_id=None),
        "board_article_id 누락",
        id="API_BAD_002_board_article_id_missing",
        marks=pytest.mark.tc(**API_BAD_002_TC),
    ),
    pytest.param(
        "API_BAD_003",
        board_article_delete_data(board_article_id=""),
        "board_article_id 빈 문자열",
        id="API_BAD_003_board_article_id_empty",
        marks=pytest.mark.tc(**API_BAD_003_TC),
    ),
    pytest.param(
        "API_BAD_004",
        board_article_delete_data(board_article_id="abc"),
        "board_article_id 문자열",
        id="API_BAD_004_board_article_id_string",
        marks=pytest.mark.tc(**API_BAD_004_TC),
    ),
    pytest.param(
        "API_BAD_005",
        board_article_delete_data(board_article_id=0),
        "board_article_id 0",
        id="API_BAD_005_board_article_id_zero",
        marks=pytest.mark.tc(**API_BAD_005_TC),
    ),
    pytest.param(
        "API_BAD_006",
        board_article_delete_data(board_article_id=-1),
        "board_article_id 음수",
        id="API_BAD_006_board_article_id_negative",
        marks=pytest.mark.tc(**API_BAD_006_TC),
    ),
    pytest.param(
        "API_BAD_007",
        board_article_delete_data(board_article_id=999999999),
        "존재하지 않는 board_article_id",
        id="API_BAD_007_board_article_id_not_found",
        marks=pytest.mark.tc(**API_BAD_007_TC),
    ),
    pytest.param(
        "API_BAD_012",
        board_article_delete_data(board_article_id="1.5"),
        "board_article_id 실수형 문자열",
        id="API_BAD_012_board_article_id_float",
        marks=pytest.mark.tc(**API_BAD_012_TC),
    ),
    pytest.param(
        "API_BAD_013",
        board_article_delete_data(board_article_id=9223372036854775808),
        "board_article_id 매우 큰 정수",
        id="API_BAD_013_board_article_id_huge",
        marks=pytest.mark.tc(**API_BAD_013_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, data, title", BOARD_ARTICLE_ID_CASES)
def test_delete_board_article_id_validation(
    api_client,
    tc_id: str,
    data: dict,
    title: str,
) -> None:
    """board_article_id의 누락, 타입 오류, 경계값과 미존재 값은 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_delete_article(data=data)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    logger.info("[%s] %s | form-data 전송", tc_id, title)
    logger.debug("form-data=%s", data)
    assert_board_article_delete_failed(response)
