# 교육자 과목 목록 조회 GET /org/{org}/course/list API 테스트 — EDU_016

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_016_TC = dict(id="EDU_016", group="Positive", title="교육자 과목 목록 조회", expected="_result ok, courses 포함")


@pytest.mark.tc(**EDU_016_TC)
def test_course_list(api_client):
    """[EDU_016] 교육자 과목 목록 조회
    내용 : 교육자(tc05) 권한으로 '과목 목록 조회(GET)' API를 호출하면
    _result ok와 함께 courses 배열이 반환되어야 한다."""
    logger.info("▶ [EDU_016] 교육자 과목 목록 조회")
    body = assert_rest_result_ok(CourseEduPage(api_client).get_course_list())
    assert "courses" in body
    logger.info("  └ 과목 %s개", body.get("course_count"))
