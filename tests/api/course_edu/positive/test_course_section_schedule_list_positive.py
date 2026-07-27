# 수업 일정 목록 조회 GET /org/{org}/course/section/schedule/list API 테스트 — EDU_007

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_007_TC = dict(id="EDU_007", group="Positive", title="수업 일정 목록 조회", expected="_result ok, section_schedules 포함")


@pytest.mark.tc(**EDU_007_TC)
def test_section_schedule_list(api_client, section_id):
    """수업 일정 (org/course/section/schedule/list)."""
    logger.info("▶ [EDU_007] 수업 일정 조회 시작 (section_id=%s)", section_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_section_schedule_list(course_section_id=section_id))
    assert "section_schedules" in body
    logger.info("  └ 일정 %s개", body.get("section_schedule_count"))


