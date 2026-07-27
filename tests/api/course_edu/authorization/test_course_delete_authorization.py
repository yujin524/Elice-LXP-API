# 클래스룸 과목 삭제 DELETE /classroom/{classroom_id}/course/{course_id} API 테스트 — EDU_B_005

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api
AUTH_FAILURE_STATUS = {401, 403, 404, 409}
NONEXISTENT_COURSE_ID = 999_999_999

EDU_B_009_TC = dict(id="EDU_B_009", group="Authority Boundary", title="학습자 토큰으로 과목 삭제 차단", expected="HTTP 4xx (권한 없음/거부)")


class TestCourseDeleteAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_009_TC)
    def test_course_edu_learner_cannot_delete_course(self, learner_api_client, classroom_id):
        """[EDU_B_009] 학습자 토큰으로 교육자 전용 과목 삭제 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '과목 삭제(DELETE)' API를 호출하면
        4xx로 거부되어야 한다. (실수로 실제 과목이 지워지지 않도록 없는 course_id로 시도)"""
        logger.info("▶ [EDU_B_009] 학습자 과목 삭제 차단 검증 (없는 course_id=%s)", NONEXISTENT_COURSE_ID)
        resp = CourseEduPage(learner_api_client).delete_course(classroom_id=classroom_id, course_id=NONEXISTENT_COURSE_ID)
        logger.info("  └ 응답 수신: status=%s (기대: 4xx 거부)", resp.status_code)
        assert resp.status_code in AUTH_FAILURE_STATUS, (
            f"삭제가 거부되지 않음! status={resp.status_code}"
        )

