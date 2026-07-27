# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_002 ~ 006, 021 ~ 022

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_article_list, assert_response_status

logger = logging.getLogger(__name__)


API_AR_002_TC = dict(id="API_AR_002", group="Validation - count", title="게시글 목록 count=1 조회", expected="200, 목록 개수 1개 이하")
API_AR_003_TC = dict(id="API_AR_003", group="Validation - count", title="count 없음", expected="422")
API_AR_004_TC = dict(id="API_AR_004", group="Validation - count", title="count 음수", expected="422")
API_AR_005_TC = dict(id="API_AR_005", group="Validation - count", title="count 문자열", expected="422")
API_AR_006_TC = dict(id="API_AR_006", group="Validation - count", title="count 최대값 초과", expected="422")
API_AR_021_TC = dict(id="API_AR_021", group="Validation - count", title="count 0", expected="200, 빈 JSON 배열")
API_AR_022_TC = dict(id="API_AR_022", group="Validation - count", title="count 서버 최대값 40 초과", expected="422")

COUNT_CASES = [
    pytest.param(
        "API_AR_002",
        board_article_list_params(count=1),
        200,
        "게시글 목록 count=1 조회",
        id="API_AR_002_count_one",
        marks=pytest.mark.tc(**API_AR_002_TC),
    ),
    pytest.param(
        "API_AR_003",
        board_article_list_params(count=None),
        422,
        "count 없음",
        id="API_AR_003_count_missing",
        marks=pytest.mark.tc(**API_AR_003_TC),
    ),
    pytest.param(
        "API_AR_004",
        board_article_list_params(count=-1),
        422,
        "count 음수",
        id="API_AR_004_count_negative",
        marks=pytest.mark.tc(**API_AR_004_TC),
    ),
    pytest.param(
        "API_AR_005",
        board_article_list_params(count="abc"),
        422,
        "count 문자열",
        id="API_AR_005_count_string",
        marks=pytest.mark.tc(**API_AR_005_TC),
    ),
    pytest.param(
        "API_AR_006",
        board_article_list_params(count=101),
        422,
        "count 최대값 초과",
        id="API_AR_006_count_too_large",
        marks=pytest.mark.tc(**API_AR_006_TC),
    ),
    pytest.param(
        "API_AR_021",
        board_article_list_params(count=0),
        200,
        "count 0",
        id="API_AR_021_count_zero",
        marks=pytest.mark.tc(**API_AR_021_TC),
    ),
    pytest.param(
        "API_AR_022",
        board_article_list_params(count=100),
        422,
        "count 서버 최대값 40 초과",
        id="API_AR_022_count_maximum",
        marks=pytest.mark.tc(**API_AR_022_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, params, expected_status, title", COUNT_CASES)
def test_get_article_list_count_validation(
    api_client,
    classroom_id: str,
    tc_id: str,
    params,
    expected_status: int,
    title: str,
) -> None:
    """
    TC ID: API_AR_002, API_AR_003, API_AR_004, API_AR_005, API_AR_006
    시나리오: 게시글 목록 조회(GET) API의 count 값으로 정상값, 누락값, 음수,
    문자열 또는 최대 허용값 초과 값을 전달하면 각 조건에 맞는 응답이 반환되어야 한다.
    """
    response = get_article_list(api_client, classroom_id=classroom_id, params=params)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    if expected_status == 200:
        assert_article_list(response, classroom_id, max_count=params["count"])
        return

    assert_response_status(response, expected_status, f"{tc_id} | {title}")
