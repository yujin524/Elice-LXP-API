# 수업 편집 POST /org/lecture/edit API 테스트 — EDU_B_001, 004

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_B_001_TC = dict(id="EDU_B_001", group="Authority Boundary", title="학습자 토큰으로 수업 편집 차단", expected="_result fail (권한 없음)")
EDU_B_002_TC = dict(id="EDU_B_002", group="Authority Boundary", title="학습자 토큰으로 수업 생성 차단", expected="_result fail (권한 없음)")


class TestLectureEditAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_001_TC)
    def test_course_edu_learner_cannot_edit_lecture(self, learner_api_client, editable_lecture):
        """[EDU_B_001] 학습자 토큰으로 교육자 전용 수업 편집 차단
        내용 : 학습자(le05) 권한으로 교육자 전용인 '수업 편집(POST)' API를 호출하면
        _result fail(권한 없음)로 차단되어야 한다."""
        course_id, lecture = editable_lecture
        lecture_id = lecture.get("id") or lecture.get("lecture_id")
        logger.info("▶ [EDU_B_001] 학습자 수업 편집 차단 검증 (lecture_id=%s)", lecture_id)
        resp = CourseEduPage(learner_api_client).edit_lecture(course_id=course_id,
            lecture_id=lecture_id,
            lecture_type=lecture.get("lecture_type", 0),
            title=lecture.get("title") or "x",  # 현재 값 유지 (혹시 통과해도 no-op)
            description=lecture.get("description") or "",
            is_opened=bool(lecture.get("is_opened")),
            is_preview=bool(lecture.get("is_preview")),
        )
        assert_rest_result_failed(resp)

    @pytest.mark.tc(**EDU_B_002_TC)
    def test_course_edu_learner_cannot_create_lecture(self, learner_api_client, course_id):
        """[EDU_B_002] 학습자 토큰으로 교육자 전용 수업 생성 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '수업 생성(POST, lecture_id 없이)' API를
        호출하면 _result fail(권한 없음)로 차단되어야 한다. (막히므로 실제로 생성되지 않음)"""
        logger.info("▶ [EDU_B_002] 학습자 수업 생성 차단 검증 (course_id=%s)", course_id)
        # payload 구성 (lecture_id 없음 = 생성 시도)
        resp = CourseEduPage(learner_api_client).edit_lecture(course_id=course_id,
            lecture_type=0,
            title="권한없는_학습자_수업생성_시도",
            description="학습자 토큰으로 수업 생성 API 호출",
        )
        assert_rest_result_failed(resp)

