# 반 전체 평균 조회 GET /classroom/{classroom_id} (dashboard) API 테스트 — API_CH_024, 025

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_response_status, assert_response_time
from tests.api.common.params import NOT_FOUND_CLASSROOM_ID

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_024_TC = dict(id="API_CH_024", group="Validation - classroom_id", title="classroom_id 빈값 요청", expected="HTTP 4xx, hang 없음")
API_CH_025_TC = dict(id="API_CH_025", group="Validation - classroom_id", title="존재하지 않는 classroom_id", expected="500 아님")

CLASSROOM_AVERAGE_4XX = {400, 401, 403, 404, 409, 422}


@pytest.mark.tc(**API_CH_024_TC)
def test_get_classroom_average_empty_classroom_id(classroom_dashboard_page) -> None:
    """classroom_id 빈 값 요청은 hang 없이 빠르게 4xx로 거부되어야 한다. (CH_002 회귀 체크 - 프로덕션에서 hang 확인 이력 있음)"""
    response = classroom_dashboard_page.get_classroom_average(None)

    logger.info("[API_CH_024] classroom_id 빈값 응답 status=%s", response.status_code)
    assert_response_time(response, 3.0, "API_CH_024 | empty classroom_id")
    assert_response_status(response, CLASSROOM_AVERAGE_4XX, "API_CH_024 | empty classroom_id")


@pytest.mark.tc(**API_CH_025_TC)
def test_get_classroom_average_nonexistent_classroom_id(classroom_dashboard_page) -> None:
    """형식은 유효하나 실존하지 않는 classroom_id는 404 또는 빈 데이터로 처리되어야 하며, 500이면 안 된다."""
    response = classroom_dashboard_page.get_classroom_average(NOT_FOUND_CLASSROOM_ID)

    logger.info("[API_CH_025] 존재하지 않는 classroom_id 응답 status=%s", response.status_code)
    assert response.status_code != 500
