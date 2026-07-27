# 수업 일정 등록 POST /schedule API 테스트 — API_CS_025

import logging
import pytest
from apis.schedule_api.schedule import SchedulePostPage
from tests.api.common.assertions import assert_response_status
from tests.api.common.payload import schedule_create_payload


logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_025_TC = dict(id="API_CS_025", group="Authentication", title="x-elice-org-name-short 헤더 누락", expected="HTTP 409, elice_calendar_server_failed 오류")
API_CS_029_TC = dict(id="API_CS_029", group="Authorization", title="학습자 토큰으로 교육자 API 호출", expected="HTTP 403, has_no_permission",)


@pytest.mark.tc(**API_CS_025_TC)
def test_educator_cannot_create_schedule_without_org_header(api_client_factory, access_token, classroom_id,):
    """[API_CS_025] x-elice-org-name-short 헤더 누락
    내용 : 교육자 계정으로 '수업 일정 등록(POST)' API를 x-elice-org-name-short 헤더 없이
    호출하면 409 Conflict와 함께 elice_calendar_server_failed 오류가 반환되어야 한다."""
    logger.info("[API_CS_025] org 헤더 없이 수업 일정 등록 요청")

    client = api_client_factory(access_token=access_token, include_org=False)
    payload = schedule_create_payload(classroom_id)

    response = SchedulePostPage(client).create_schedule(**payload)

    logger.info("수업 일정 등록 org 헤더 누락 응답 status=%s", response.status_code)
    logger.debug("수업 일정 등록 org 헤더 누락 응답 body=%s", response.text)

    assert_response_status(response, 409, "API_CS_025 | x-elice-org-name-short 헤더 누락")

    body = response.json()

    assert body["code"] == "elice_calendar_server_failed", (f"예상과 다른 오류 코드: {response.text}")

    assert body["detail"]["method"] == "POST", f"예상과 다른 method: {body!r}"
    assert body["detail"]["path"] == "/schedule", f"예상과 다른 path: {body!r}"

    logger.info("org 헤더 누락 오류 코드 확인: %s", body["code"])


@pytest.mark.tc(**API_CS_029_TC)
def test_learner_cannot_create_schedule_with_learner_token(learner_schedule_post_page, classroom_id,):
    """[API_CS_029] 학습자 토큰으로 교육자 API 호출
    내용 : 학습자 토큰으로 교육자 권한이 필요한 '수업 일정 등록(POST)' API를 호출하면
    403 Forbidden 응답이 반환되어야 한다.
    """
    logger.info("[API_CS_029] 학습자 토큰으로 수업 일정 등록 요청")

    payload = schedule_create_payload(classroom_id)

    response = learner_schedule_post_page.create_schedule(**payload)

    logger.info("학습자 토큰 수업 일정 등록 응답 status=%s", response.status_code)
    logger.debug("학습자 토큰 수업 일정 등록 응답 body=%s", response.text)

    assert response.status_code == 403, (
        f"학습자 토큰으로 교육자 API 호출이 차단되지 않음! "
        f"상태 코드: {response.status_code}, 응답: {response.text}"
    )

    body = response.json()

    assert body.get("code") == "has_no_permission", (f"예상과 다른 오류 코드: {response.text}")

    assert body.get("message") == "You have no permission", (f"예상과 다른 오류 메시지: {response.text}")

    logger.info("학습자 토큰 권한 차단 확인: %s", body.get("code"))
