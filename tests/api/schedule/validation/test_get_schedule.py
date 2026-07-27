# 수업 일정 목록 조회 GET /schedule API 테스트 — API_CS_003 ~ 007, 010 ~ 011

import logging
import pytest
from tests.api.common.assertions import format_error_detail
from tests.api.common.params import (
    INVALID_CLASSROOM_ID,
    NOT_FOUND_CLASSROOM_ID,
    SCHEDULE_INVALID_DT_START_GE,
    SCHEDULE_INVALID_DT_START_LE,
    schedule_list_params,
)

logger = logging.getLogger(__name__)

API_CS_003_TC = dict(id="API_CS_003", group="Validation", title="classroom_id 누락", expected="HTTP 422, classroom_id 필수값 누락 오류")
API_CS_004_TC = dict(id="API_CS_004", group="Validation", title="dt_start_ge 누락", expected="HTTP 422, dt_start_ge 필수값 누락 오류")
API_CS_005_TC = dict(id="API_CS_005", group="Validation", title="dt_start_le 누락", expected="HTTP 422, dt_start_le 필수값 누락 오류")
API_CS_006_TC = dict(id="API_CS_006", group="Validation", title="count 누락", expected="HTTP 422, count 필수값 누락 오류")
API_CS_007_TC = dict(id="API_CS_007", group="Validation", title="날짜 범위 오류", expected="HTTP 409, elice_calendar_unexpected_result 오류, 내부 code=invalid_datetime_format")
API_CS_010_TC = dict(id="API_CS_010", group="Validation", title="존재하지 않는 classroom_id", expected="HTTP 409, model_not_found 오류")
API_CS_011_TC = dict(id="API_CS_011", group="Validation", title="classroom_id 형식 오류", expected="HTTP 422, uuid_parsing 오류")


@pytest.mark.parametrize(
    "tc_id, missing_param",
    [
        pytest.param(
            "API_CS_003",
            "classroom_id",
            marks=pytest.mark.tc(**API_CS_003_TC),
            id="API_CS_003",
        ),
        pytest.param(
            "API_CS_004",
            "dt_start_ge",
            marks=pytest.mark.tc(**API_CS_004_TC),
            id="API_CS_004",
        ),
        pytest.param(
            "API_CS_005",
            "dt_start_le",
            marks=pytest.mark.tc(**API_CS_005_TC),
            id="API_CS_005",
        ),
        pytest.param(
            "API_CS_006",
            "count",
            marks=pytest.mark.tc(**API_CS_006_TC),
            id="API_CS_006",
        ),
    ],
)
def test_learner_cannot_get_schedule_list_without_required_query_param(
    schedule_page,
    classroom_id,
    tc_id,
    missing_param,
):
    """[API_CS_003~006] 필수 query parameter 누락
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 필수 query parameter 없이
    호출하면 422 Unprocessable Entity와 함께 missing 오류가 반환되어야 한다."""
    logger.info("[%s] 필수 query parameter 누락 요청: %s", tc_id, missing_param)

    params = schedule_list_params(classroom_id)
    params.pop(missing_param)

    response = schedule_page.get_schedule_list(**params)

    logger.info("schedule 필수값 누락 응답 status=%s", response.status_code)

    assert response.status_code == 422, (
        f"{missing_param} 누락이 걸러지지 않음! 상태 코드: {response.status_code}"
    )

    detail = response.json()["detail"][0]

    assert detail["type"] == "missing", f"예상과 다른 오류 타입: {detail!r}"
    assert missing_param in detail["loc"], f"{missing_param} 필드를 가리키지 않음: {detail!r}"

    logger.info("%s 누락 검증 결과: %s", missing_param, format_error_detail(detail))


@pytest.mark.tc(**API_CS_007_TC)
def test_learner_cannot_get_schedule_list_with_invalid_date_range(
    schedule_page,
    classroom_id,
):
    """[API_CS_007] 날짜 범위 오류
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 dt_start_ge가 dt_start_le보다
    늦은 날짜 범위로 호출하면 409 Conflict와 함께 날짜 형식 관련 오류가 반환되어야 한다."""
    logger.info("[API_CS_007] 잘못된 날짜 범위로 일정 목록 조회 요청")

    response = schedule_page.get_schedule_list(
        **schedule_list_params(
            classroom_id,
            dt_start_ge=SCHEDULE_INVALID_DT_START_GE,
            dt_start_le=SCHEDULE_INVALID_DT_START_LE,
        )
    )

    logger.info("schedule 날짜 범위 오류 응답 status=%s", response.status_code)

    assert response.status_code == 409, (
        f"날짜 범위 오류 응답이 예상과 다름! 상태 코드: {response.status_code}, 응답: {response.text}"
    )

    body = response.json()

    assert body["code"] == "elice_calendar_unexpected_result", f"예상과 다른 오류 코드: {response.text}"

    inner_error = body["detail"]["resp_json"]

    assert inner_error["code"] == "invalid_datetime_format", f"예상과 다른 내부 오류 코드: {body!r}"

    logger.info("날짜 범위 오류 확인: code=%s, inner_code=%s", body["code"], inner_error["code"])


@pytest.mark.parametrize(
    "tc_id, classroom_id_value, expected_status, expected_error_type, expected_error_code",
    [
        pytest.param(
            "API_CS_010",
            NOT_FOUND_CLASSROOM_ID,
            409,
            None,
            "model_not_found",
            marks=pytest.mark.tc(**API_CS_010_TC),
            id="API_CS_010",
        ),
        pytest.param(
            "API_CS_011",
            INVALID_CLASSROOM_ID,
            422,
            "uuid_parsing",
            None,
            marks=pytest.mark.tc(**API_CS_011_TC),
            id="API_CS_011",
        ),
    ],
)
def test_learner_cannot_get_schedule_list_with_invalid_classroom_id(
    schedule_page,
    tc_id,
    classroom_id_value,
    expected_status,
    expected_error_type,
    expected_error_code,
):
    """[API_CS_010~011] classroom_id 오류
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 존재하지 않는 classroom_id
    또는 UUID 형식이 아닌 classroom_id로 호출하면 각 오류 유형에 맞는 상태 코드와
    오류 응답이 반환되어야 한다."""
    logger.info("[%s] 잘못된 classroom_id로 일정 목록 조회 요청", tc_id)

    response = schedule_page.get_schedule_list(**schedule_list_params(classroom_id_value))

    logger.info("schedule classroom_id 오류 응답 status=%s", response.status_code)

    assert response.status_code == expected_status, (
        f"classroom_id 오류 응답이 예상과 다름! "
        f"상태 코드: {response.status_code}, 응답: {response.text}"
    )

    body = response.json()

    if expected_error_code:
        assert body["code"] == expected_error_code, f"예상과 다른 오류 코드: {response.text}"
        logger.info("존재하지 않는 classroom_id 오류 코드: %s", body["code"])

    if expected_error_type:
        detail = body["detail"][0]

        assert detail["type"] == expected_error_type, f"예상과 다른 오류 타입: {detail!r}"
        assert "classroom_id" in detail["loc"], f"classroom_id 필드를 가리키지 않음: {detail!r}"

        logger.info("classroom_id 형식 오류 detail=%s", format_error_detail(detail))
