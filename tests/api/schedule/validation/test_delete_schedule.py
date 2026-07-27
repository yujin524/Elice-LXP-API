# 일정 삭제 DELETE /schedule/{schedule_id} API 테스트 — API_CH_029

import logging
import pytest

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_029_TC = dict(id="API_CH_029", group="Validation", title="DELETE classroom_id 누락", expected="HTTP 422")


@pytest.mark.tc(**API_CH_029_TC)
def test_delete_schedule_missing_classroom_id(schedule_id_page, created_schedule_id: str) -> None:
    """[API_CH_029] classroom_id 없이 DELETE 시도 시 HTTP 422가 반환되어야 한다."""
    logger.info("[API_CH_029] classroom_id 없이 일정 삭제 요청 (schedule_id=%s)", created_schedule_id)

    response = schedule_id_page.delete_schedule(schedule_id=created_schedule_id)

    logger.info("응답 status=%s", response.status_code)
    assert response.status_code == 422
