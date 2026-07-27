# 수업 일정 미리보기 GET /schedule/by_date API 테스트 — API_CH_010 ~ 014

from __future__ import annotations
import datetime
import logging
import pytest
from apis.schedule_api.schedule_by_date import ScheduleByDatePage
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import schedule_by_date_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CH_010_TC = dict(id="API_CH_010", group="Negative", title="date 파라미터 누락", expected="HTTP 422")
CH_011_TC = dict(id="API_CH_011", group="Negative", title="classroom_id 누락", expected="HTTP 422")
CH_012_TC = dict(id="API_CH_012", group="Negative", title="x-elice-org-name-short 헤더 누락", expected="HTTP 409")
CH_013_TC = dict(id="API_CH_013", group="Negative", title="date 형식 오류(슬래시 구분자)", expected="HTTP 422")
CH_014_TC = dict(id="API_CH_014", group="Negative", title="존재하지 않는 날짜", expected="HTTP 422")


@pytest.mark.parametrize(
    "tc_id, missing_param",
    [
        pytest.param("API_CH_010", "date", marks=pytest.mark.tc(**CH_010_TC), id="API_CH_010"),
        pytest.param("API_CH_011", "classroom_id", marks=pytest.mark.tc(**CH_011_TC), id="API_CH_011"),
    ],
)
def test_get_schedule_by_date_missing_required_param(
    schedule_by_date_page, classroom_id, tc_id, missing_param
):
    """[API_CH_010, API_CH_011] 필수 query parameter 누락
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    date 또는 classroom_id 없이 호출하면 422 상태 코드가 반환되어야 한다."""
    params = schedule_by_date_params(classroom_id, date=datetime.date.today().isoformat())
    params.pop(missing_param)

    logger.info("[%s] %s 없이 수업 일정 미리보기 조회 요청", tc_id, missing_param)
    response = schedule_by_date_page.get_schedule_by_date(**params)
    logger.info("%s 누락 응답 status=%s", missing_param, response.status_code)

    assert_response_status(response, 422, f"{missing_param} 누락")


@pytest.mark.tc(**CH_012_TC)
def test_get_schedule_by_date_without_org_header(api_client_factory, access_token: str, classroom_id):
    """[API_CH_012] x-elice-org-name-short 헤더 누락
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    필수 헤더(org) 없이 호출하면 409 상태 코드가 반환되어야 한다."""
    today = datetime.date.today().isoformat()
    logger.info("[API_CH_012] org 헤더 없이 수업 일정 미리보기 조회 요청")
    client = api_client_factory(access_token=access_token, include_org=False)
    response = ScheduleByDatePage(client).get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date=today)
    )
    logger.info("org 헤더 누락 응답 status=%s", response.status_code)

    assert_response_status(response, 409, "org 헤더 누락")


@pytest.mark.tc(**CH_013_TC)
def test_get_schedule_by_date_invalid_date_format(schedule_by_date_page, classroom_id):
    """[API_CH_013] date 형식 오류(슬래시 구분자)
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    YYYY-MM-DD가 아닌 형식(예: 2026/07/14)으로 호출하면 422 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_013] 슬래시 구분자 date로 수업 일정 미리보기 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026/07/14")
    )
    logger.info("date 형식 오류 응답 status=%s", response.status_code)

    assert_response_status(response, 422, "date 형식 오류")


@pytest.mark.tc(**CH_014_TC)
def test_get_schedule_by_date_nonexistent_calendar_date(schedule_by_date_page, classroom_id):
    """[API_CH_014] 존재하지 않는 날짜
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    달력상 존재하지 않는 날짜(예: 2026-02-30)로 호출하면 422 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_014] 존재하지 않는 날짜로 수업 일정 미리보기 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-02-30")
    )
    logger.info("존재하지 않는 날짜 응답 status=%s", response.status_code)

    assert_response_status(response, 422, "존재하지 않는 날짜")

