# 수업 일정 ICS 파일 조회 GET /schedule/ics API 테스트 — API_CS_017

import logging
import pytest
from tests.api.common.assertions import assert_schedule_ics
from tests.api.common.params import schedule_ics_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_017_TC = dict(id="API_CS_017", group="Positive", title="ICS 파일 정상 조회", expected="HTTP 200, ICS 형식 응답")


@pytest.mark.tc(**API_CS_017_TC)
def test_learner_can_get_schedule_ics(
    schedule_ics_page,
    classroom_id,
):
    """[API_CS_017] ICS 파일 정상 조회
    내용 : 학습자(qatrack) 계정으로 '일정 ICS 조회(GET)' API를 정상적인 classroom_id와
    날짜 범위로 호출하면 200 OK와 함께 ICS 캘린더 형식의 응답이 반환되어야 한다."""
    logger.info("[API_CS_017] 일정 ICS 파일 정상 조회 요청")

    response = schedule_ics_page.get_schedule_ics(**schedule_ics_params(classroom_id))

    logger.info("schedule ics 응답 status=%s", response.status_code)

    body = assert_schedule_ics(response)
    logger.info("schedule ics 응답 길이: %d", len(body))
