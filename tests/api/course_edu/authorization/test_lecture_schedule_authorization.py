# 수업 일정 설정 POST /org/lecture/schedule API 테스트 — EDU_B_008

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

_DUMMY_OPEN_MS = 1900000000000
_DUMMY_CLOSE_MS = 1900000060000
logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_B_005_TC = dict(id="EDU_B_005", group="Authority Boundary", title="학습자 토큰으로 수업 일정 설정 차단", expected="_result fail (권한 없음)")


class TestLectureScheduleAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_005_TC)
    def test_course_edu_learner_cannot_set_lecture_schedule(self, learner_api_client, lecture_id):
        """[EDU_B_005] 학습자 토큰으로 교육자 전용 수업 일정 설정 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '수업 공개/마감 일정 설정(POST)' API를
        호출하면 _result fail(권한 없음)로 차단되어야 한다. (막히므로 일정이 바뀌지 않음)"""
        logger.info("▶ [EDU_B_005] 학습자 수업 일정 설정 차단 검증 (lecture_id=%s)", lecture_id)
        resp = CourseEduPage(learner_api_client).set_lecture_schedule(lecture_id=lecture_id,
            open_schedule_datetime=_DUMMY_OPEN_MS,
            close_schedule_datetime=_DUMMY_CLOSE_MS,
        )
        assert_rest_result_failed(resp)

