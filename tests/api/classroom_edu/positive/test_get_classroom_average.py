# 반 전체 평균 조회 GET /classroom/{classroom_id} (dashboard) API 테스트 — API_CH_022

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_classroom_average

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_022_TC = dict(id="API_CH_022", group="Positive", title="반 전체 평균 조회", expected="HTTP 200")


@pytest.mark.tc(**API_CH_022_TC)
def test_get_classroom_average_success(classroom_dashboard_page, classroom_id: str) -> None:
    """교육자 계정, 정상 classroom_id로 반 전체 평균을 조회하면 200과 함께 평균 정보를 반환한다."""
    logger.info("▶ [API_CH_022] 반 전체 평균 조회 시작 (classroom_id=%s)", classroom_id)
    response = classroom_dashboard_page.get_classroom_average(classroom_id)

    assert_classroom_average(response, classroom_id)
