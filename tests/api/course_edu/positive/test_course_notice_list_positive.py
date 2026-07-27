# 과목 공지 목록 조회 GET /org/{org}/course/notice/list API 테스트 — EDU_004

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_004_TC = dict(id="EDU_004", group="Positive", title="과목 공지 목록 조회", expected="_result ok, course_notices 포함")


@pytest.mark.tc(**EDU_004_TC)
def test_notice_list(api_client, course_id):
    """과목 공지 관리 (org/course/notice/list)."""
    logger.info("▶ [EDU_004] 공지 목록 조회 시작 (course_id=%s)", course_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_notice_list(course_id=course_id))
    assert "course_notices" in body
    logger.info("  └ 공지 %s개", body.get("course_notice_count"))


