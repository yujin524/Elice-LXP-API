# 수업 일정 목록 조회 GET /schedule API 테스트 — API_CS_008 ~ 009

import logging
import pytest
from apis.schedule_api.schedule import SchedulePage
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import schedule_list_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_008_TC = dict(id="API_CS_008", group="Authentication", title="Authorization 헤더 누락", expected="HTTP 401/403")
API_CS_009_TC = dict(id="API_CS_009", group="Authentication", title="x-elice-org-name-short 헤더 누락", expected="HTTP 409")


@pytest.mark.tc(**API_CS_008_TC)
def test_learner_cannot_get_schedule_list_without_authorization(
    api_client_factory,
    classroom_id,
):
    """[API_CS_008] Authorization 헤더 누락
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 Authorization 헤더 없이
    호출하면 인증 실패 응답이 반환되어야 한다."""
    logger.info("[API_CS_008] Authorization 헤더 없이 일정 목록 조회 요청")

    client = api_client_factory(include_auth=False)
    response = SchedulePage(client).get_schedule_list(**schedule_list_params(classroom_id))

    logger.info("schedule 인증 실패 응답 status=%s", response.status_code)
    assert_response_status(response, {401, 403}, "API_CS_008 | Authorization 헤더 누락")


@pytest.mark.tc(**API_CS_009_TC)
def test_learner_cannot_get_schedule_list_without_org_header(
    api_client_factory,
    access_token: str,
    classroom_id,
):
    """[API_CS_009] x-elice-org-name-short 헤더 누락
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 x-elice-org-name-short 헤더 없이
    호출하면 409 Conflict와 함께 elice_calendar_server_failed 오류가 반환되어야 한다."""
    logger.info("[API_CS_009] org 헤더 없이 일정 목록 조회 요청")

    client = api_client_factory(access_token=access_token, include_org=False)
    response = SchedulePage(client).get_schedule_list(**schedule_list_params(classroom_id))

    logger.info("schedule org 헤더 누락 응답 status=%s", response.status_code)
    assert_response_status(response, 409, "API_CS_009 | x-elice-org-name-short 헤더 누락")

    body = response.json()

    assert body["code"] == "elice_calendar_server_failed", f"예상과 다른 오류 코드: {response.text}"

    logger.info("org 헤더 누락 오류 코드: %s", body["code"])
