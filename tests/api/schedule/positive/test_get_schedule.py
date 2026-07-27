# 수업 일정 목록 조회 GET /schedule API 테스트 — API_CS_001 ~ 002

import logging
import pytest
from tests.api.common.assertions import assert_schedule_list
from tests.api.common.params import SCHEDULE_MIN_COUNT, schedule_list_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_001_TC = dict(id="API_CS_001", group="Positive", title="일정 목록 정상 조회", expected="HTTP 200, 배열 응답")
API_CS_002_TC = dict(id="API_CS_002", group="Positive", title="count=1 최소값 경계 검증", expected="HTTP 200, 배열 응답, 응답 개수 1개 이하")


@pytest.mark.tc(**API_CS_001_TC)
def test_learner_can_get_schedule_list(
    schedule_page,
    classroom_id,
):
    """[API_CS_001] 일정 목록 정상 조회
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 정상적인 classroom_id,
    날짜 범위, count 값으로 호출하면 200 OK와 함께 배열이 반환되어야 한다."""
    logger.info("[API_CS_001] 일정 목록 정상 조회 요청")

    response = schedule_page.get_schedule_list(**schedule_list_params(classroom_id))

    logger.info("schedule 목록 응답 status=%s", response.status_code)

    body = assert_schedule_list(response)
    logger.info("schedule 목록 %d건 조회됨", len(body))


@pytest.mark.tc(**API_CS_002_TC)
def test_learner_can_get_schedule_list_with_count_minimum(
    schedule_page,
    classroom_id,
):
    """[API_CS_002] count=1 최소값 경계 검증
    내용 : 학습자(qatrack) 계정으로 '일정 목록 조회(GET)' API를 count=1로 호출하면
    200 OK와 함께 배열이 반환되고, 응답 데이터 개수는 1개 이하여야 한다."""
    logger.info("[API_CS_002] count=1 조건으로 일정 목록 조회 요청")

    response = schedule_page.get_schedule_list(
        **schedule_list_params(classroom_id, count=SCHEDULE_MIN_COUNT)
    )

    logger.info("schedule count=1 응답 status=%s", response.status_code)

    body = assert_schedule_list(response, max_count=1)
    logger.info("schedule count=1 조회 결과: %d건", len(body))
