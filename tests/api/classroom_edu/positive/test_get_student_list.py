# 학생별 현황 리스트 조회 GET /student (dashboard) API 테스트 — API_CH_023

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_student_list

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_023_TC = dict(id="API_CH_023", group="Positive", title="학생별 현황 리스트 조회", expected="HTTP 200")


@pytest.mark.tc(**API_CH_023_TC)
def test_get_student_list_success(classroom_dashboard_page, classroom_id: str) -> None:
    """교육자 계정, 학생별 현황 리스트를 조회하면 200과 함께 학생 리스트를 반환한다."""
    logger.info("▶ [API_CH_023] 학생별 현황 리스트 조회 시작 (classroom_id=%s)", classroom_id)
    response = classroom_dashboard_page.get_student_list(classroom_id=classroom_id, offset=0, count=10)

    students = assert_student_list(response, max_count=10)
    logger.info("  └ 학생 %d명 조회됨", len(students))
