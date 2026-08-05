# 수업 일정 생성 후 조회 및 삭제 시나리오 테스트 — API_CS_030

import logging
from uuid import uuid4
import pytest
from tests.api.common.assertions import (assert_schedule_list, assert_schedule_mutation_success)
from tests.api.common.params import schedule_list_params
from tests.api.common.payload import schedule_create_payload


logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_030_TC = dict(id="API_CS_030", group="Scenario", title="수업 일정 생성 후 조회 및 삭제", expected="일정 생성 후 목록 조회에서 확인되고, 이후 삭제된다.",)


@pytest.mark.tc(**API_CS_030_TC)
def test_schedule_create_read_delete_scenario(schedule_id_page, schedule_page, classroom_id: str) -> None:
    """[API_CS_030] 수업 일정 생성 후 조회 및 삭제
    내용: 교육자 계정으로 수업 일정을 생성한 뒤 목록 조회에서 확인하고, 생성한 일정을 삭제한다.
    """
    schedule_id = None
    deleted = False

    logger.info("[API_CS_030] 수업 일정 생성 요청")

    payload = schedule_create_payload(classroom_id, summary=f"api_scenario_schedule_{uuid4().hex[:8]}")

    create_response = schedule_id_page.create_schedule(**payload)

    logger.info("수업 일정 생성 응답 status=%s", create_response.status_code)
    logger.debug("수업 일정 생성 응답 body=%s", create_response.text)

    assert_schedule_mutation_success(create_response, "API_CS_030 | create schedule")

    try:
        logger.info("[API_CS_030] 생성한 수업 일정 조회 요청")

        list_response = schedule_page.get_schedule_list(**schedule_list_params(classroom_id, count=50))

        logger.info("수업 일정 목록 조회 응답 status=%s", list_response.status_code)

        schedules = assert_schedule_list(list_response, max_count=50)

        created_schedule = next(
            (
                schedule
                for schedule in schedules
                if schedule.get("summary") == payload["summary"]
                and schedule.get("dt_start") == payload["dt_start"]
            ),
            None,
        )

        assert created_schedule is not None, (
            f"생성한 수업 일정을 목록에서 찾지 못함! "
            f"summary={payload['summary']}, dt_start={payload['dt_start']}"
        )

        schedule_id = created_schedule["id"]

        logger.info("생성한 수업 일정 조회 확인 schedule_id=%s", schedule_id)

        logger.info("[API_CS_030] 생성한 수업 일정 삭제 요청")

        delete_response = schedule_id_page.delete_schedule(schedule_id=schedule_id, classroom_id=classroom_id)

        logger.info("수업 일정 삭제 응답 status=%s", delete_response.status_code)

        assert_schedule_mutation_success(delete_response, "API_CS_030 | delete schedule")

        deleted = True

        logger.info("[API_CS_030] 수업 일정 생성 후 조회 및 삭제 시나리오 완료")

    finally:
        if schedule_id is not None and not deleted:
            cleanup_response = schedule_id_page.delete_schedule(schedule_id=schedule_id, classroom_id=classroom_id)

            logger.info("시나리오 테스트 cleanup 실행 schedule_id=%s, status=%s", schedule_id, cleanup_response.status_code)
