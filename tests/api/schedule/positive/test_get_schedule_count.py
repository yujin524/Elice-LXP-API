# 수업 일정 개수 조회 GET /schedule/count API 테스트 — API_CS_012

import logging
import pytest
from tests.api.common.assertions import assert_schedule_count
from tests.api.common.params import schedule_count_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_012_TC = dict(id="API_CS_012", group="Positive", title="일정 개수 정상 조회", expected="HTTP 200, count 정수 응답")


@pytest.mark.tc(**API_CS_012_TC)
def test_learner_can_get_schedule_count(
    schedule_count_page,
    classroom_id,
):
    """[API_CS_012] 일정 개수 정상 조회
    내용 : 학습자(qatrack) 계정으로 '일정 개수 조회(GET)' API를 정상적인 classroom_id와
    날짜 범위로 호출하면 200 OK와 함께 일정 개수 값이 반환되어야 한다."""
    logger.info("[API_CS_012] 일정 개수 정상 조회 요청")

    response = schedule_count_page.get_schedule_count(**schedule_count_params(classroom_id))

    logger.info("schedule count 응답 status=%s", response.status_code)

    count_value = assert_schedule_count(response)
    logger.info("schedule count 조회 결과: %s", count_value)
