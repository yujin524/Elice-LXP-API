import logging
import os
from uuid import uuid4

import pytest

from apis.schedule_api.schedule import SchedulePage, SchedulePostPage
from apis.schedule_api.schedule_id import ScheduleIdPage
from tests.api.common.assertions import assert_schedule_list, assert_schedule_mutation_success
from tests.api.common.params import schedule_list_params
from tests.api.common.payload import schedule_create_payload
from utils.auth_token import get_token

logger = logging.getLogger(__name__)

LEARNER_ID = os.getenv("LEARNER_ID", "").strip()
LEARNER_PW = os.getenv("LEARNER_PW", "")


@pytest.fixture
def schedule_page(api_client):
    """Schedule 조회 API 객체."""
    return SchedulePage(api_client)


@pytest.fixture
def schedule_post_page(api_client):
    """Schedule 등록 API 객체."""
    return SchedulePostPage(api_client)


@pytest.fixture
def schedule_id_page(api_client):
    """Schedule ID 기반 수정/삭제 API 객체."""
    return ScheduleIdPage(api_client)


@pytest.fixture(scope="session")
def learner_access_token() -> str:
    """학습자 계정으로 access_token을 발급받는다."""
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
    """학습자 토큰으로 요청하는 SchedulePostPage."""
    client = api_client_factory(access_token=learner_access_token)
    return SchedulePostPage(client)


@pytest.fixture
def created_schedule_id(schedule_post_page, schedule_page, schedule_id_page, classroom_id: str):
    """수정/삭제 테스트에서 사용할 테스트용 일정을 생성하고 schedule_id를 반환한다."""
    summary = f"api_test_schedule_{uuid4().hex[:8]}"

    payload = schedule_create_payload(
        classroom_id,
        summary=summary,
    )

    create_response = schedule_post_page.create_schedule(**payload)

    assert_schedule_mutation_success(
        create_response,
        "created_schedule_id | create schedule",
    )

    list_response = schedule_page.get_schedule_list(
        **schedule_list_params(
            classroom_id,
            count=50,
        )
    )

    schedules = assert_schedule_list(
        list_response,
        max_count=50,
    )

    created_schedule = next(
        (
            schedule
            for schedule in schedules
            if schedule.get("summary") == summary
            and schedule.get("dt_start") == payload["dt_start"]
        ),
        None,
    )

    assert created_schedule is not None, (
        f"생성한 테스트 일정을 목록에서 찾지 못함! "
        f"summary={summary}, dt_start={payload['dt_start']}"
    )

    schedule_id = created_schedule["id"]

    logger.info("[준비] created_schedule_id 확보: %s", schedule_id)

    yield schedule_id

    cleanup_response = schedule_id_page.delete_schedule(
        schedule_id=schedule_id,
        classroom_id=classroom_id,
    )

    if cleanup_response.status_code != 200:
        logger.warning(
            "[정리] 테스트용 일정 삭제 실패: schedule_id=%s, status=%s",
            schedule_id,
            cleanup_response.status_code,
        )