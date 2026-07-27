# 라이브 강의실 생성 POST /org/course/lectureroom/edit API 테스트 — EDU_B_007

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_B_007_TC = dict(id="EDU_B_007", group="Authority Boundary", title="학습자 토큰으로 라이브 강의실 생성 차단", expected="_result fail (권한 없음)")


class TestCourseLectureroomEditAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_007_TC)
    def test_course_edu_learner_cannot_create_lectureroom(self, learner_api_client, course_id, section_id):
        """[EDU_B_007] 학습자 토큰으로 교육자 전용 라이브 강의실 생성 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '라이브 강의실 생성(POST)' API를 호출하면
        _result fail(권한 없음)로 차단되어야 한다. (막히므로 실제로 강의실이 생성되지 않음)"""
        logger.info("▶ [EDU_B_007] 학습자 라이브 강의실 생성 차단 검증 (course_id=%s)", course_id)
        resp = CourseEduPage(learner_api_client).create_lectureroom(course_id=course_id,
            course_section_id=section_id,
            title="권한없는_학습자_강의실생성_시도",
        )
        assert_rest_result_failed(resp)

