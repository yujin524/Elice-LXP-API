# 수강생 목록 조회 GET /org/{org}/course/user/list API 테스트 — EDU_003

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_003_TC = dict(id="EDU_003", group="Positive", title="수강생 목록 조회", expected="_result ok, users 포함")


@pytest.mark.tc(**EDU_003_TC)
def test_course_user_list(api_client, course_id):
    """수강생 목록 (org/course/user/list)."""
    logger.info("▶ [EDU_003] 수강생 목록 조회 시작 (course_id=%s)", course_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_course_user_list(course_id=course_id))
    assert "users" in body
    logger.info("  └ 수강생 %s명", body.get("user_count"))


