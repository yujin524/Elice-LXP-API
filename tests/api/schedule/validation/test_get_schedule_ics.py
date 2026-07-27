# 수업 일정 ICS 파일 조회 GET /schedule/ics API 테스트 — API_CS_018, 020

import logging
import pytest
from tests.api.common.assertions import format_error_detail
from tests.api.common.params import INVALID_CLASSROOM_ID, schedule_ics_params

logger = logging.getLogger(__name__)

API_CS_018_TC = dict(id="API_CS_018", group="Validation", title="필수 query parameter 누락", expected="HTTP 422, missing 오류")
API_CS_020_TC = dict(id="API_CS_020", group="Validation", title="classroom_id 형식 오류", expected="HTTP 422, uuid_parsing 오류")


@pytest.mark.tc(**API_CS_018_TC)
def test_learner_cannot_get_schedule_ics_without_required_query_param(
    schedule_ics_page,
    classroom_id,
):
    """[API_CS_018] 필수 query parameter 누락
    내용 : 학습자(qatrack) 계정으로 '일정 ICS 조회(GET)' API를 필수 query parameter인
    dt_start_ge 없이 호출하면 422 Unprocessable Entity와 함께 missing 오류가 반환되어야 한다."""
    logger.info("[API_CS_018] dt_start_ge 누락 상태로 일정 ICS 조회 요청")

    response = schedule_ics_page.get_schedule_ics(
        **schedule_ics_params(classroom_id, dt_start_ge=None)
    )

    logger.info("schedule ics 필수값 누락 응답 status=%s", response.status_code)

    assert response.status_code == 422, f"dt_start_ge 누락이 걸러지지 않음! 상태 코드: {response.status_code}"

    detail = response.json()["detail"][0]

    assert detail["type"] == "missing", f"예상과 다른 오류 타입: {detail!r}"
    assert "dt_start_ge" in detail["loc"], f"dt_start_ge 필드를 가리키지 않음: {detail!r}"

    logger.info("dt_start_ge 누락 검증 결과: %s", format_error_detail(detail))


@pytest.mark.tc(**API_CS_020_TC)
def test_learner_cannot_get_schedule_ics_with_invalid_classroom_id_format(
    schedule_ics_page,
):
    """[API_CS_020] classroom_id 형식 오류
    내용 : 학습자(qatrack) 계정으로 '일정 ICS 조회(GET)' API를 UUID 형식이 아닌
    classroom_id로 호출하면 422 Unprocessable Entity와 함께 uuid_parsing 오류가 반환되어야 한다."""
    logger.info("[API_CS_020] UUID 형식이 아닌 classroom_id로 일정 ICS 조회 요청")

    response = schedule_ics_page.get_schedule_ics(**schedule_ics_params(INVALID_CLASSROOM_ID))

    logger.info("schedule ics classroom_id 형식 오류 응답 status=%s", response.status_code)

    assert response.status_code == 422, f"classroom_id 형식 오류가 걸러지지 않음! 상태 코드: {response.status_code}"

    detail = response.json()["detail"][0]

    assert detail["type"] == "uuid_parsing", f"예상과 다른 오류 타입: {detail!r}"
    assert "classroom_id" in detail["loc"], f"classroom_id 필드를 가리키지 않음: {detail!r}"

    logger.info("classroom_id 형식 오류 detail=%s", format_error_detail(detail))
