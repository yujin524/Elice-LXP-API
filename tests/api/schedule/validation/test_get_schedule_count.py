# 수업 일정 개수 조회 GET /schedule/count API 테스트 — API_CS_013 ~ 014, 016

import logging
import pytest
from tests.api.common.assertions import format_error_detail
from tests.api.common.params import (
    INVALID_CLASSROOM_ID,
    SCHEDULE_INVALID_DT_START_GE,
    SCHEDULE_INVALID_DT_START_LE,
    schedule_count_params,
)

logger = logging.getLogger(__name__)

API_CS_013_TC = dict(id="API_CS_013", group="Validation", title="필수 query parameter 누락", expected="HTTP 422, missing 오류")
API_CS_014_TC = dict(id="API_CS_014", group="Validation", title="날짜 범위 오류", expected="HTTP 409, elice_calendar_unexpected_result 오류, 내부 code=invalid_datetime_format")
API_CS_016_TC = dict(id="API_CS_016", group="Validation", title="classroom_id 형식 오류", expected="HTTP 422, uuid_parsing 오류")


@pytest.mark.tc(**API_CS_013_TC)
def test_learner_cannot_get_schedule_count_without_required_query_param(
    schedule_count_page,
    classroom_id,
):
    """[API_CS_013] 필수 query parameter 누락
    내용 : 학습자(qatrack) 계정으로 '일정 개수 조회(GET)' API를 필수 query parameter인
    dt_start_ge 없이 호출하면 422 Unprocessable Entity와 함께 missing 오류가 반환되어야 한다."""
    logger.info("[API_CS_013] dt_start_ge 누락 상태로 일정 개수 조회 요청")

    response = schedule_count_page.get_schedule_count(
        **schedule_count_params(classroom_id, dt_start_ge=None)
    )

    logger.info("schedule count 필수값 누락 응답 status=%s", response.status_code)

    assert response.status_code == 422, f"dt_start_ge 누락이 걸러지지 않음! 상태 코드: {response.status_code}"

    detail = response.json()["detail"][0]

    assert detail["type"] == "missing", f"예상과 다른 오류 타입: {detail!r}"
    assert "dt_start_ge" in detail["loc"], f"dt_start_ge 필드를 가리키지 않음: {detail!r}"

    logger.info("dt_start_ge 누락 검증 결과: %s", format_error_detail(detail))


@pytest.mark.tc(**API_CS_014_TC)
def test_learner_cannot_get_schedule_count_with_invalid_date_range(
    schedule_count_page,
    classroom_id,
):
    """[API_CS_014] 날짜 범위 오류
    내용 : 학습자(qatrack) 계정으로 '일정 개수 조회(GET)' API를 dt_start_ge가 dt_start_le보다
    늦은 날짜 범위로 호출하면 409 Conflict와 함께 날짜 형식 관련 오류가 반환되어야 한다."""
    logger.info("[API_CS_014] 잘못된 날짜 범위로 일정 개수 조회 요청")

    response = schedule_count_page.get_schedule_count(
        **schedule_count_params(
            classroom_id,
            dt_start_ge=SCHEDULE_INVALID_DT_START_GE,
            dt_start_le=SCHEDULE_INVALID_DT_START_LE,
        )
    )

    logger.info("schedule count 날짜 범위 오류 응답 status=%s", response.status_code)

    assert response.status_code == 409, (
        f"날짜 범위 오류 응답이 예상과 다름! 상태 코드: {response.status_code}, 응답: {response.text}"
    )

    body = response.json()

    assert body["code"] == "elice_calendar_unexpected_result", f"예상과 다른 오류 코드: {response.text}"

    inner_error = body["detail"]["resp_json"]

    assert inner_error["code"] == "invalid_datetime_format", f"예상과 다른 내부 오류 코드: {body!r}"

    logger.info("날짜 범위 오류 확인: code=%s, inner_code=%s", body["code"], inner_error["code"])


@pytest.mark.tc(**API_CS_016_TC)
def test_learner_cannot_get_schedule_count_with_invalid_classroom_id_format(
    schedule_count_page,
):
    """[API_CS_016] classroom_id 형식 오류
    내용 : 학습자(qatrack) 계정으로 '일정 개수 조회(GET)' API를 UUID 형식이 아닌
    classroom_id로 호출하면 422 Unprocessable Entity와 함께 uuid_parsing 오류가 반환되어야 한다."""
    logger.info("[API_CS_016] UUID 형식이 아닌 classroom_id로 일정 개수 조회 요청")

    response = schedule_count_page.get_schedule_count(**schedule_count_params(INVALID_CLASSROOM_ID))

    logger.info("schedule count classroom_id 형식 오류 응답 status=%s", response.status_code)

    assert response.status_code == 422, f"classroom_id 형식 오류가 걸러지지 않음! 상태 코드: {response.status_code}"

    detail = response.json()["detail"][0]

    assert detail["type"] == "uuid_parsing", f"예상과 다른 오류 타입: {detail!r}"
    assert "classroom_id" in detail["loc"], f"classroom_id 필드를 가리키지 않음: {detail!r}"

    logger.info("classroom_id 형식 오류 detail=%s", format_error_detail(detail))
