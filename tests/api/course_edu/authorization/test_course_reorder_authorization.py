# 클래스룸 과목 순서 변경 POST /classroom/{classroom_id}/course/reorder API 테스트 — EDU_B_003

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api
AUTH_FAILURE_STATUS = {401, 403, 404, 409}

EDU_B_008_TC = dict(id="EDU_B_008", group="Authority Boundary", title="학습자 토큰으로 과목 순서 변경 차단", expected="HTTP 401/403/409 (권한 없음)")


class TestCourseReorderAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_008_TC)
    def test_course_edu_learner_cannot_reorder_course(self, learner_api_client, api_client, classroom_id):
        """[EDU_B_008] 학습자 토큰으로 교육자 전용 과목 순서 변경 차단
        내용 : 학습자(le05) 권한으로 교육자 전용인 '과목 순서 변경(POST)' API를 호출하면
        HTTP 401/403/409(권한 없음)로 차단되어야 한다."""
        # 정상(교육자) client로 현재 순서를 읽어, 학생 client에는 동일 순서(no-op)를 보낸다.
        # (reorder는 전체 course_id 집합과 정확히 일치해야 하므로 페이징 끝까지 모은다)
        courses = CourseEduPage(api_client).list_all_classroom_courses(classroom_id=classroom_id)
        current_order = [c["course_id"] for c in courses]

        logger.info("▶ [EDU_B_008] 학습자 과목 순서 변경 차단 검증 (classroom_id=%s)", classroom_id)
        resp = CourseEduPage(learner_api_client).reorder_courses(classroom_id=classroom_id, course_ids=current_order)
        logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
        assert_response_status(resp, AUTH_FAILURE_STATUS, "EDU_B_008 학습자 토큰 과목 순서 변경 차단")

