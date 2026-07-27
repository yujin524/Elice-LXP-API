# 커리큘럼 섹션 목록 조회 GET /org/{org}/course/section/list API 테스트 — EDU_002

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_002_TC = dict(id="EDU_002", group="Positive", title="커리큘럼(섹션) 목록 조회", expected="_result ok, course_sections 포함")


@pytest.mark.tc(**EDU_002_TC)
def test_section_list(api_client, course_id):
    """커리큘럼(섹션) 구조 (org/course/section/list)."""
    logger.info("▶ [EDU_002] 섹션 목록 조회 시작 (course_id=%s)", course_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_section_list(course_id=course_id))
    assert "course_sections" in body
    logger.info("  └ 섹션 %s개", body.get("course_section_count"))


