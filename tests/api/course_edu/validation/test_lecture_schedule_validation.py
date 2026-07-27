# 수업 일정 설정 검증 POST /org/{org}/lecture/schedule API 테스트 — EDU_N_029

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_029_TC = dict(id="EDU_N_029", group="Validation - Query Params", title="수업 일정 설정 - 없는 lecture_id", expected="_result fail")


@pytest.mark.tc(**EDU_N_029_TC)
def test_set_schedule_nonexistent_lecture(api_client):
    """없는 lecture_id로 수업 일정 설정 -> 거부 (대상이 없어 아무것도 안 바뀜)."""
    logger.info("▶ [EDU_N_029] 없는 lecture_id=%s 로 수업 일정 설정 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).set_lecture_schedule(lecture_id=NONEXISTENT_ID,
        open_schedule_datetime=1900000000000,
        close_schedule_datetime=1900000060000,
    )
    assert_rest_result_failed(resp)


