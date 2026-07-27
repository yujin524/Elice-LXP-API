# 강의 목록 조회 GET /org/{org}/lecture/list API 테스트 — EDU_006

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_006_TC = dict(id="EDU_006", group="Positive", title="강의 목록 조회", expected="_result ok, lectures 포함")


@pytest.mark.tc(**EDU_006_TC)
def test_lecture_list(api_client, course_id):
    """강의 목록 (org/lecture/list)."""
    logger.info("▶ [EDU_006] 강의 목록 조회 시작 (course_id=%s)", course_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_lecture_list(course_id=course_id))
    assert "lectures" in body
    logger.info("  └ 강의 %s개", body.get("lecture_count"))


