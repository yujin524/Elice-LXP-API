# 과목 상세 조회 GET /org/{org}/course/get API 테스트 — EDU_001

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_001_TC = dict(id="EDU_001", group="Positive", title="과목 상세 조회(편집 화면 로드)", expected="_result ok, course 포함")


@pytest.mark.tc(**EDU_001_TC)
def test_course_detail(api_client, course_id):
    """과목 상세 - 편집 화면 로드 (org/course/get)."""
    logger.info("▶ [EDU_001] 과목 상세 조회 시작 (course_id=%s)", course_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_course_detail(course_id=course_id))
    assert "course" in body
    logger.info("  └ 과목 제목: %s", body["course"].get("title"))


