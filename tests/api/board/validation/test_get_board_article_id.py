# 게시글 상세 조회 GET /board/article/get API 테스트 — API_BA_002 ~ 006, 011 ~ 013

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_params
from tests.api.common.assertions import assert_board_article_get_failed

logger = logging.getLogger(__name__)


API_BA_002_TC = dict(id="API_BA_002", group="Validation - board_article_id", title="board_article_id 없음", expected="422")
API_BA_003_TC = dict(id="API_BA_003", group="Validation - board_article_id", title="board_article_id 문자열", expected="422")
API_BA_004_TC = dict(id="API_BA_004", group="Validation - board_article_id", title="board_article_id 음수", expected="400/404/409/422, 500 미만")
API_BA_005_TC = dict(id="API_BA_005", group="Validation - board_article_id", title="board_article_id 0", expected="400/404/409/422, 500 미만")
API_BA_006_TC = dict(id="API_BA_006", group="Validation - board_article_id", title="존재하지 않는 board_article_id", expected="400/404/409/422, 500 미만")
API_BA_011_TC = dict(id="API_BA_011", group="Validation - board_article_id", title="board_article_id 빈 문자열", expected="422")
API_BA_012_TC = dict(id="API_BA_012", group="Validation - board_article_id", title="board_article_id 실수형 문자열", expected="422")
API_BA_013_TC = dict(id="API_BA_013", group="Validation - board_article_id", title="board_article_id 매우 큰 정수", expected="400/404/409/422, 500 미만")

INVALID_BOARD_ARTICLE_STATUSES = {400, 404, 409, 422}

BOARD_ARTICLE_ID_CASES = [
    pytest.param(
        "API_BA_002",
        board_article_params(board_article_id=None),
        422,
        "board_article_id 없음",
        id="API_BA_002_board_article_id_missing",
        marks=pytest.mark.tc(**API_BA_002_TC),
    ),
    pytest.param(
        "API_BA_003",
        board_article_params(board_article_id="abc"),
        422,
        "board_article_id 문자열",
        id="API_BA_003_board_article_id_string",
        marks=pytest.mark.tc(**API_BA_003_TC),
    ),
    pytest.param(
        "API_BA_004",
        board_article_params(board_article_id=-1),
        INVALID_BOARD_ARTICLE_STATUSES,
        "board_article_id 음수",
        id="API_BA_004_board_article_id_negative",
        marks=pytest.mark.tc(**API_BA_004_TC),
    ),
    pytest.param(
        "API_BA_005",
        board_article_params(board_article_id=0),
        INVALID_BOARD_ARTICLE_STATUSES,
        "board_article_id 0",
        id="API_BA_005_board_article_id_zero",
        marks=pytest.mark.tc(**API_BA_005_TC),
    ),
    pytest.param(
        "API_BA_006",
        board_article_params(board_article_id=999999999),
        INVALID_BOARD_ARTICLE_STATUSES,
        "존재하지 않는 board_article_id",
        id="API_BA_006_board_article_id_not_found",
        marks=pytest.mark.tc(**API_BA_006_TC),
    ),
    pytest.param(
        "API_BA_011",
        board_article_params(board_article_id=""),
        422,
        "board_article_id 빈 문자열",
        id="API_BA_011_board_article_id_empty",
        marks=pytest.mark.tc(**API_BA_011_TC),
    ),
    pytest.param(
        "API_BA_012",
        board_article_params(board_article_id="1.5"),
        422,
        "board_article_id 실수형 문자열",
        id="API_BA_012_board_article_id_float",
        marks=pytest.mark.tc(**API_BA_012_TC),
    ),
    pytest.param(
        "API_BA_013",
        board_article_params(board_article_id=9223372036854775808),
        INVALID_BOARD_ARTICLE_STATUSES,
        "board_article_id 매우 큰 정수",
        id="API_BA_013_board_article_id_huge",
        marks=pytest.mark.tc(**API_BA_013_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, params, expected_status, title", BOARD_ARTICLE_ID_CASES)
def test_get_board_article_id_validation(
    api_client,
    tc_id: str,
    params,
    expected_status,
    title: str,
) -> None:
    """
    TC ID: API_BA_002, API_BA_003, API_BA_004, API_BA_005, API_BA_006
    시나리오: board_article_id query parameter에 누락값, 문자열, 음수, 0 또는
    존재하지 않는 값을 전달하면 각 조건에 맞는 응답이 반환되어야 한다.
    """
    response = OrgBoardArticleApi(api_client).get_article(params=params)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    logger.info("[%s] %s | expected=%s", tc_id, title, expected_status)
    assert_board_article_get_failed(response)
