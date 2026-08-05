# 일정 수정 PATCH /schedule/{schedule_id} API 테스트 — API_CH_027

import logging
import pytest
from tests.api.common.assertions import assert_schedule_mutation_success

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_027_TC = dict(id="API_CH_027", group="Positive", title="정상 일정 수정", expected="HTTP 200")


@pytest.mark.tc(**API_CH_027_TC)
def test_edit_schedule_success(schedule_id_page, classroom_id: str, created_schedule_id: str) -> None:
    """[API_CH_027] 정상 일정 수정
    내용: 사전에 생성한 테스트용 일정을, 정상 classroom_id와 함께 수정하면 200 OK를 반환해야 한다."""
    logger.info("[API_CH_027] 일정 수정 요청 (schedule_id=%s)", created_schedule_id)

    response = schedule_id_page.update_schedule(
        schedule_id=created_schedule_id,
        classroom_id=classroom_id,
        summary="test_edited_by_api",
    )

    logger.info("일정 수정 응답 status=%s", response.status_code)
    assert_schedule_mutation_success(response, "API_CH_027 | edit schedule")
