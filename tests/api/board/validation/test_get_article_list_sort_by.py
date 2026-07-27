# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_024 ~ 025

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)


API_AR_024_TC = dict(id="API_AR_024", group="Validation - sort_by", title="sort_by 누락", expected="200, 기본 정렬로 JSON 배열 반환")
API_AR_025_TC = dict(id="API_AR_025", group="Validation - sort_by", title="sort_by 허용값 외 문자열", expected="422")

SORT_BY_CASES = [
    pytest.param(
        "API_AR_024",
        board_article_list_params(sort_by=None),
        200,
        "sort_by 누락",
        id="API_AR_024_sort_by_missing",
        marks=pytest.mark.tc(**API_AR_024_TC),
    ),
    pytest.param(
        "API_AR_025",
        board_article_list_params(sort_by="invalid"),
        422,
        "sort_by 허용값 외 문자열",
        id="API_AR_025_sort_by_invalid",
        marks=pytest.mark.tc(**API_AR_025_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, params, expected_status, title", SORT_BY_CASES)
def test_get_article_list_sort_by_validation(
    api_client,
    classroom_id: str,
    tc_id: str,
    params: dict,
    expected_status: int,
    title: str,
) -> None:
    """sort_by 누락은 기본값으로 처리되고 허용값 외 문자열은 거부되어야 한다."""
    response = get_article_list(api_client, classroom_id=classroom_id, params=params)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    assert_response_status(response, expected_status, f"{tc_id} | {title}")
    if expected_status == 200:
        assert isinstance(response.json(), list)
