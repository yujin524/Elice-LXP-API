# 수업 일정 미리보기 GET /schedule/by_date API 테스트 — API_CH_015, 017 ~ 018, 021

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import schedule_by_date_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CH_015_TC = dict(id="API_CH_015", group="Boundary", title="일정 없는 날짜 조회", expected="HTTP 200, schedules 배열이 비어있음")
CH_017_TC = dict(id="API_CH_017", group="Boundary", title="tags 하위 필드 누락 케이스", expected="HTTP 200")
CH_018_TC = dict(id="API_CH_018", group="Boundary", title="lectureroom_id null 케이스", expected="HTTP 200")
CH_021_TC = dict(id="API_CH_021", group="Boundary", title="다건 일정(9개) 조회", expected="HTTP 200, schedules 9건")


@pytest.mark.tc(**CH_015_TC)
def test_get_schedule_by_date_no_schedule(schedule_by_date_page, classroom_id):
    """[API_CH_015] 일정 없는 날짜 조회
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    일정이 없는 날짜(결과 0건 경계)로 호출하면 200 상태 코드와 함께 빈 schedules 배열이 반환되어야 한다."""
    logger.info("[API_CH_015] 일정 없는 날짜로 수업 일정 미리보기 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2050-01-01")
    )
    logger.info("일정 없는 날짜 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "일정 없는 날짜 조회")

    body = response.json()
    if isinstance(body, list) and body and body[0].get("schedules"):
        assert len(body[0]["schedules"]) == 0, f"일정이 없어야 하는데 존재함: {body!r}"


@pytest.mark.tc(**CH_017_TC)
def test_get_schedule_by_date_tags_missing(schedule_by_date_page, classroom_id):
    """[API_CH_017] tags 하위 필드 누락 케이스
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    tags 하위 필드가 없는 일정이 포함된 날짜로 호출하면 200 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_017] tags 필드 누락 일정이 있는 날짜로 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-07-14")
    )
    logger.info("tags 누락 케이스 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "tags 필드 누락 케이스 조회")


@pytest.mark.tc(**CH_018_TC)
def test_get_schedule_by_date_non_live_lecture(schedule_by_date_page, classroom_id):
    """[API_CH_018] lectureroom_id null 케이스
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    라이브 강의가 아닌 일정이 있는 날짜로 호출하면 200 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_018] 라이브 강의가 아닌 일정이 있는 날짜로 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-06-30")
    )
    logger.info("non-live 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "non-live 일정 조회")


@pytest.mark.tc(**CH_021_TC)
def test_get_schedule_by_date_many_schedules(schedule_by_date_page, classroom_id):
    """[API_CH_021] 다건 일정(9개) 조회
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    일정이 9개 등록된 날짜(다건 경계)로 호출하면 200 상태 코드와 함께 schedules 9건이 반환되어야 한다."""
    logger.info("[API_CH_021] 일정 9개 등록된 날짜로 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-07-08")
    )
    logger.info("다건 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "다건 일정 조회")

    body = response.json()
    if isinstance(body, list) and body and body[0].get("schedules"):
        assert len(body[0]["schedules"]) == 9, f"9건이 아님: {len(body[0]['schedules'])}건"

