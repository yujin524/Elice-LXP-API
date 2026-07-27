"""Schedule API 테스트 전용 fixture 모음."""

import os
import logging
from utils.auth_token import get_token
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from apis.schedule_api.schedule import (
    LectureroomPage,
    ScheduleCountPage,
    ScheduleIcsPage,
    SchedulePage,
    SchedulePostPage,
)
from apis.schedule_api.schedule_by_date import ScheduleByDatePage
from apis.schedule_api.schedule_id import ScheduleIdPage

logger = logging.getLogger(__name__)

LEARNER_ID = os.getenv("LEARNER_ID", "").strip()
LEARNER_PW = os.getenv("LEARNER_PW", "")


@pytest.fixture
def schedule_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 SchedulePage."""
    return SchedulePage(api_client)


@pytest.fixture
def schedule_id_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 ScheduleIdPage (일정 생성/수정/삭제)."""
    return ScheduleIdPage(api_client)


@pytest.fixture
def created_schedule_id(schedule_page, schedule_id_page, classroom_id: str):
    """테스트용 일정을 생성하고 id를 확보합니다. (CH_027~031 - 생성 응답 body가 비어있어 목록 조회로 id 확보)

    테스트 종료 후에는 정리 차원에서 삭제를 시도하되, 테스트가 이미 삭제했다면 실패해도 무시합니다.
    """
    summary = f"api_test_schedule_{uuid4().hex[:8]}"
    dt_start = datetime.now(timezone.utc) + timedelta(days=7)
    dt_end = dt_start + timedelta(hours=1)

    create_resp = schedule_id_page.create_schedule(
        classroom_id=classroom_id,
        summary=summary,
        dt_start=dt_start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        dt_end=dt_end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    )
    assert create_resp.status_code in (200, 201), f"테스트용 일정 생성 실패: status={create_resp.status_code}"

    list_resp = schedule_page.get_schedule_list(
        classroom_id=classroom_id,
        dt_start_ge=dt_start.strftime("%Y-%m-%dT00:00:00Z"),
        dt_start_le=(dt_start + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z"),
        count=50,
    )
    assert list_resp.status_code == 200, f"일정 목록 조회 실패: status={list_resp.status_code}"
    match = next((item for item in list_resp.json() if item.get("summary") == summary), None)
    if match is None:
        pytest.skip("생성한 테스트용 일정을 목록에서 찾지 못했습니다. (반영 지연 가능)")

    schedule_id = match["id"]
    logger.info("[준비] created_schedule_id 확보: %s", schedule_id)
    yield schedule_id

    cleanup_resp = schedule_id_page.delete_schedule(schedule_id=schedule_id, classroom_id=classroom_id)
    if cleanup_resp.status_code not in (200, 204, 404):
        logger.warning("[정리] 테스트용 일정 삭제 실패: schedule_id=%s, status=%s", schedule_id, cleanup_resp.status_code)


@pytest.fixture
def schedule_count_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 ScheduleCountPage."""
    return ScheduleCountPage(api_client)


@pytest.fixture
def schedule_ics_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 ScheduleIcsPage."""
    return ScheduleIcsPage(api_client)


@pytest.fixture
def schedule_by_date_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 ScheduleByDatePage."""
    return ScheduleByDatePage(api_client)


@pytest.fixture
def lectureroom_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 LectureroomPage."""
    return LectureroomPage(api_client)


@pytest.fixture(scope="session")
def lectureroom_id() -> int:
    """강의실 상세 조회 테스트에서 사용하는 고정 lectureroom_id."""
    return 145931


@pytest.fixture
def schedule_post_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 SchedulePostPage."""
    return SchedulePostPage(api_client)


@pytest.fixture(scope="session")
def learner_access_token() -> str:
    """학습자 계정으로 로그인해 access_token을 발급받는다. (권한 경계 테스트 전용)"""
    if not LEARNER_ID or not LEARNER_PW:
        pytest.skip("학습자 계정 정보가 없어 권한 경계 테스트를 Skip합니다. (LEARNER_ID/LEARNER_PW)")

    try:
        token = get_token(LEARNER_ID, LEARNER_PW)
    except RuntimeError as exc:
        pytest.skip(f"학습자 계정 로그인 실패({LEARNER_ID}): {exc}")

    logger.info("[준비] 학습자(learner) 토큰 발급 완료: %s", LEARNER_ID)
    return token


@pytest.fixture
def learner_schedule_post_page(api_client_factory, learner_access_token):
    """학습자 토큰으로 요청하는 SchedulePostPage. (권한 경계 테스트 전용)"""
    client = api_client_factory(access_token=learner_access_token)
    return SchedulePostPage(client)