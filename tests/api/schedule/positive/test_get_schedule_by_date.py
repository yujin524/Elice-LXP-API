# 수업 일정 미리보기 GET /schedule/by_date API 테스트 — API_CH_009, 016, 019 ~ 020

from __future__ import annotations
import datetime
import logging
import pytest
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import schedule_by_date_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CH_009_TC = dict(id="API_CH_009", group="Positive", title="오늘 날짜로 정상 조회", expected="HTTP 200")
CH_016_TC = dict(id="API_CH_016", group="Positive", title="dt_start vs display_dt_start 검증", expected="HTTP 200 (필드값은 별도 수동 대조 필요)")
CH_019_TC = dict(id="API_CH_019", group="Positive", title="is_live_lecture/is_in_progress 검증", expected="HTTP 200")
CH_020_TC = dict(id="API_CH_020", group="Positive", title="summary 이모지/특수문자 확인", expected="HTTP 200")


@pytest.mark.tc(**CH_009_TC)
def test_get_schedule_by_date_today(schedule_by_date_page, classroom_id):
    """[API_CH_009] 오늘 날짜로 정상 조회
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    오늘 날짜로 호출하면 200 상태 코드가 반환되어야 한다."""
    today = datetime.date.today().isoformat()
    logger.info("[API_CH_009] 오늘 날짜로 수업 일정 미리보기 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date=today)
    )
    logger.info("오늘 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "오늘 일정 조회")


@pytest.mark.tc(**CH_016_TC)
def test_get_schedule_by_date_allday_schedule(schedule_by_date_page, classroom_id):
    """[API_CH_016] dt_start vs display_dt_start 검증
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    종일 일정이 있는 날짜로 호출하면 200 상태 코드가 반환되어야 한다.
    (dt_start/display_dt_start 값 비교는 별도 수동 대조 필요)"""
    logger.info("[API_CH_016] 종일 일정이 있는 날짜로 수업 일정 미리보기 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-07-14")
    )
    logger.info("종일 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "종일 일정 조회")


@pytest.mark.tc(**CH_019_TC)
def test_get_schedule_by_date_mixed_status(schedule_by_date_page, classroom_id):
    """[API_CH_019] is_live_lecture/is_in_progress 검증
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    진행 중/예정 일정이 함께 있는 날짜로 호출하면 200 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_019] 진행 중/예정 일정이 함께 있는 날짜로 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-07-14")
    )
    logger.info("혼합 상태 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "혼합 상태 일정 조회")


@pytest.mark.tc(**CH_020_TC)
def test_get_schedule_by_date_emoji_summary(schedule_by_date_page, classroom_id):
    """[API_CH_020] summary 이모지/특수문자 확인
    내용 : 학습자(qatrack) 권한으로 본인 전용인 '수업 일정 미리보기 조회(GET)' API를
    이모지가 포함된 일정명이 있는 날짜로 호출하면 200 상태 코드가 반환되어야 한다."""
    logger.info("[API_CH_020] 이모지 포함 일정명이 있는 날짜로 조회 요청")
    response = schedule_by_date_page.get_schedule_by_date(
        **schedule_by_date_params(classroom_id, date="2026-06-30")
    )
    logger.info("이모지 일정 응답 status=%s", response.status_code)

    assert_response_status(response, 200, "이모지 일정 조회")

