# 학생별 과목 학습현황 GET /student/{id}/course (dashboard) API 테스트 — EDU_017

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_017_TC = dict(id="EDU_017", group="Positive", title="학생별 과목 학습현황 조회", expected="200")


@pytest.mark.tc(**EDU_017_TC)
def test_student_course_progress(api_client, student_user_id, classroom_id):
    """[EDU_017] 학생별 과목 학습현황 조회
    내용 : 교육자(tc05) 권한으로 '학생별 과목 학습현황 조회(GET)' API를 호출하면
    200 상태 코드가 반환되어야 한다."""
    logger.info("▶ [EDU_017] 학생별 과목 학습현황 조회 (student_user_id=%s)", student_user_id)
    resp = CourseEduPage(api_client).get_student_course_progress(student_user_id=student_user_id, classroom_id=classroom_id)
    assert_response_status(resp, 200, "EDU_017 학생별 과목 학습현황 조회")
