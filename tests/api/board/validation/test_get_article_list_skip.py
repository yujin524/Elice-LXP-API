# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_007 ~ 010, 023

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)


API_AR_007_TC = dict(id="API_AR_007", group="Validation - skip", title="skip 없음", expected="422")
API_AR_008_TC = dict(id="API_AR_008", group="Validation - skip", title="skip 음수", expected="422")
API_AR_009_TC = dict(id="API_AR_009", group="Validation - skip", title="skip 문자열", expected="422")
API_AR_010_TC = dict(id="API_AR_010", group="Validation - skip", title="skip 큰 값", expected="200, JSON 배열")
API_AR_023_TC = dict(id="API_AR_023", group="Validation - skip", title="skip 최소 정상값 0", expected="200, JSON 배열")

SKIP_CASES = [
    pytest.param(
        "API_AR_007",
        board_article_list_params(skip=None),
        422,
        "skip 없음",
        id="API_AR_007_skip_missing",
        marks=pytest.mark.tc(**API_AR_007_TC),
    ),
    pytest.param(
        "API_AR_008",
        board_article_list_params(skip=-1),
        422,
        "skip 음수",
        id="API_AR_008_skip_negative",
        marks=pytest.mark.tc(**API_AR_008_TC),
    ),
    pytest.param(
        "API_AR_009",
        board_article_list_params(skip="abc"),
        422,
        "skip 문자열",
        id="API_AR_009_skip_string",
        marks=pytest.mark.tc(**API_AR_009_TC),
    ),
    pytest.param(
        "API_AR_010",
        board_article_list_params(skip=100000),
        200,
        "skip 큰 값",
        id="API_AR_010_skip_large",
        marks=pytest.mark.tc(**API_AR_010_TC),
    ),
    pytest.param(
        "API_AR_023",
        board_article_list_params(skip=0),
        200,
        "skip 최소 정상값 0",
        id="API_AR_023_skip_zero",
        marks=pytest.mark.tc(**API_AR_023_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, params, expected_status, title", SKIP_CASES)
def test_get_article_list_skip_validation(
    api_client,
    classroom_id: str,
    tc_id: str,
    params,
    expected_status: int,
    title: str,
) -> None:
    """
    TC ID: API_AR_007, API_AR_008, API_AR_009, API_AR_010
    시나리오: 게시글 목록 조회(GET) API의 skip 값으로 누락값, 음수, 문자열 또는
    큰 값을 전달하면 각 조건에 맞는 응답이 반환되어야 한다.
    """
    response = get_article_list(api_client, classroom_id=classroom_id, params=params)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_response_status(response, expected_status, f"{tc_id} | {title}")
    if expected_status == 200:
        assert isinstance(response.json(), list)
