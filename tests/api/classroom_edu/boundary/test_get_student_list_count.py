# 학생별 현황 리스트 조회 GET /student (dashboard) API 테스트 — API_CH_026

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_response_time

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_026_TC = dict(id="API_CH_026", group="Validation - count", title="count=0 경계값", expected="hang 없음, 500 아님")


@pytest.mark.tc(**API_CH_026_TC)
def test_get_student_list_count_zero(classroom_dashboard_page, classroom_id: str) -> None:
    """count=0 최소 경계값 요청은 hang 없이 빠르게 응답해야 하며, 500이면 안 된다."""
    response = classroom_dashboard_page.get_student_list(classroom_id=classroom_id, offset=0, count=0)

    logger.info("[API_CH_026] count=0 응답 status=%s", response.status_code)
    assert_response_time(response, 3.0, "API_CH_026 | count=0")
    assert response.status_code != 500
