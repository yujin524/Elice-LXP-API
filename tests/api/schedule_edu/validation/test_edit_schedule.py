# 일정 수정 PATCH /schedule/{schedule_id} API 테스트 — API_CH_028, 030

import logging
import pytest
from tests.api.common.params import NOT_FOUND_CLASSROOM_ID

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_028_TC = dict(id="API_CH_028", group="Validation", title="PATCH classroom_id 누락", expected="HTTP 422")
API_CH_030_TC = dict(id="API_CH_030", group="Validation", title="존재하지 않는 schedule_id", expected="500 아님")


@pytest.mark.tc(**API_CH_028_TC)
def test_edit_schedule_missing_classroom_id(schedule_id_page, created_schedule_id: str) -> None:
    """[API_CH_028] body에 classroom_id 생략. 스펙상 required이므로 422를 기대한다."""
    logger.info("[API_CH_028] classroom_id 누락 일정 수정 요청 (schedule_id=%s)", created_schedule_id)

    response = schedule_id_page.update_schedule(schedule_id=created_schedule_id, summary="no_classroom_id_test")

    logger.info("응답 status=%s", response.status_code)
    assert response.status_code == 422


@pytest.mark.tc(**API_CH_030_TC)
def test_edit_schedule_nonexistent_schedule_id(schedule_id_page, classroom_id: str) -> None:
    """[API_CH_030] 형식은 유효하나 실존하지 않는 schedule_id. 404 또는 명확한 에러를 기대하며, 500이면 안 된다."""
    logger.info("[API_CH_030] 존재하지 않는 schedule_id로 수정 요청")

    response = schedule_id_page.update_schedule(
        schedule_id=NOT_FOUND_CLASSROOM_ID,
        classroom_id=classroom_id,
        summary="nonexistent_test",
    )

    logger.info("응답 status=%s", response.status_code)
    assert response.status_code != 500
