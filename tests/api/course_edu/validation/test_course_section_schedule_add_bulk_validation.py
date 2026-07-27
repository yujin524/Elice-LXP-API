# 수업 일정 일괄 추가 검증 POST /org/{org}/course/section/schedule/add/bulk API 테스트 — EDU_N_026

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_026_TC = dict(id="EDU_N_026", group="Validation - Query Params", title="수업 일정 추가 - 없는 course_section_id", expected="_result fail")


@pytest.mark.tc(**EDU_N_026_TC)
def test_add_schedule_nonexistent_section(api_client):
    """없는 course_section_id로 일정 추가 -> 거부 (대상이 없어 아무것도 안 만들어짐)."""
    logger.info("▶ [EDU_N_026] 없는 course_section_id=%s 로 수업 일정 추가 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).add_section_schedules(course_section_id=NONEXISTENT_ID,
        section_schedule_list=[{"begin_datetime": 1900000000000, "end_datetime": 1900000060000}],
    )
    assert_rest_result_failed(resp)


