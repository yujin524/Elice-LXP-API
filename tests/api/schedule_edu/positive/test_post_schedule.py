# 수업 일정 등록 POST /schedule API 테스트 — API_CS_024

import logging
import pytest
from tests.api.common.payload import schedule_create_payload


logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_024_TC = dict(id="API_CS_024", group="Positive", title="수업 일정 정상 등록", expected="HTTP 200 또는 201",)


@pytest.mark.tc(**API_CS_024_TC)
def test_educator_can_create_schedule(schedule_post_page, classroom_id,):
    """[API_CS_024] 수업 일정 정상 등록
    내용 : 교육자 계정으로 '수업 일정 등록(POST)' API를 필수값이 모두 포함된 Body로 호출하면
    HTTP 200 또는 201 응답이 반환되어야 한다."""
    logger.info("[API_CS_024] 수업 일정 정상 등록 요청")

    payload = schedule_create_payload(classroom_id)

    response = schedule_post_page.create_schedule(**payload)

    logger.info("수업 일정 등록 응답 status=%s", response.status_code)
    logger.debug("수업 일정 등록 응답 body=%s", response.text)

    assert response.status_code in {200, 201}, (f"수업 일정 등록 실패! 상태 코드: {response.status_code}, 응답: {response.text}")

    body = response.json()

    assert isinstance(body, dict), f"응답 Body가 객체가 아님: {body!r}"

    logger.info("수업 일정 등록 요청 정상 처리 확인")
