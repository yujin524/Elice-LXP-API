# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_018 ~ 020, 026

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import (
    get_article_list,
    get_missing_classroom_id_route,
)
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)


API_AR_018_TC = dict(id="API_AR_018", group="Validation - classroom_id", title="잘못된 classroom_id", expected="400/403/404/422, 500 미만")
API_AR_019_TC = dict(id="API_AR_019", group="Validation - classroom_id", title="classroom_id 빈값 경로", expected="422")
API_AR_020_TC = dict(id="API_AR_020", group="Validation - classroom_id", title="classroom_id 경로 조각 누락", expected="404")
API_AR_026_TC = dict(id="API_AR_026", group="Validation - classroom_id", title="존재하지 않는 유효 UUID classroom_id", expected="400/403/404/422, 500 미만")

INVALID_CLASSROOM_STATUSES = {400, 403, 404, 409, 422}

CLASSROOM_ID_CASES = [
    pytest.param(
        "API_AR_018",
        get_article_list,
        {"classroom_id": "invalid-classroom-id", "params": board_article_list_params(count=1)},
        INVALID_CLASSROOM_STATUSES,
        "잘못된 classroom_id",
        id="API_AR_018_invalid_classroom_id",
        marks=pytest.mark.tc(**API_AR_018_TC),
    ),
    pytest.param(
        "API_AR_019",
        get_article_list,
        {"classroom_id": "", "params": board_article_list_params(count=1)},
        422,
        "classroom_id 빈값 경로",
        id="API_AR_019_empty_classroom_id",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="Expected validation error for an empty classroom_id path parameter."),
            pytest.mark.tc(**API_AR_019_TC),
        ],
    ),
    pytest.param(
        "API_AR_020",
        get_missing_classroom_id_route,
        {"params": board_article_list_params(count=1)},
        404,
        "classroom_id 경로 조각 누락",
        id="API_AR_020_missing_classroom_id_route",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="Expected route not found when classroom_id segment is omitted."),
            pytest.mark.tc(**API_AR_020_TC),
        ],
    ),
    pytest.param(
        "API_AR_026",
        get_article_list,
        {
            "classroom_id": "00000000-0000-4000-8000-000000000000",
            "params": board_article_list_params(count=1),
        },
        INVALID_CLASSROOM_STATUSES,
        "존재하지 않는 유효 UUID classroom_id",
        id="API_AR_026_nonexistent_classroom_id",
        marks=pytest.mark.tc(**API_AR_026_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, request_func, request_kwargs, expected_status, title", CLASSROOM_ID_CASES)
def test_get_article_list_classroom_id_validation(
    api_client,
    tc_id: str,
    request_func,
    request_kwargs,
    expected_status,
    title: str,
) -> None:
    """
    TC ID: API_AR_018, API_AR_019, API_AR_020
    누락 경로: GET {API_BASE_URL}/classroom/article
    시나리오: classroom_id로 잘못된 형식, 빈 값 또는 누락된 path를 전달하면
    각 조건에 맞는 제어 가능한 오류 응답이 반환되어야 한다.
    """
    response = request_func(api_client, **request_kwargs)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_response_status(response, expected_status, f"{tc_id} | {title}")
    assert response.status_code < 500
