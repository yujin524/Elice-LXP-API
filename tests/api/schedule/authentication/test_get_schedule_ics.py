# 수업 일정 ICS 파일 조회 GET /schedule/ics API 테스트 — API_CS_019

import logging
import pytest
from apis.schedule_api.schedule import ScheduleIcsPage
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import schedule_ics_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_019_TC = dict(id="API_CS_019", group="Authentication", title="Authorization 헤더 누락", expected="HTTP 401/403")


@pytest.mark.tc(**API_CS_019_TC)
def test_learner_cannot_get_schedule_ics_without_authorization(
    api_client_factory,
    classroom_id,
):
    """[API_CS_019] Authorization 헤더 누락
    내용 : 학습자(qatrack) 계정으로 '일정 ICS 조회(GET)' API를 Authorization 헤더 없이
    호출하면 인증 실패 응답이 반환되어야 한다."""
    logger.info("[API_CS_019] Authorization 헤더 없이 일정 ICS 조회 요청")

    client = api_client_factory(include_auth=False)
    response = ScheduleIcsPage(client).get_schedule_ics(**schedule_ics_params(classroom_id))

    logger.info("schedule ics 인증 실패 응답 status=%s", response.status_code)
    assert_response_status(response, {401, 403}, "API_CS_019 | Authorization 헤더 누락")
