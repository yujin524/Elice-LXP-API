# 수업 일정 일괄 추가 POST /org/course/section/schedule/add/bulk API 테스트 — EDU_B_006

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

_DUMMY_SCHEDULES = [{"begin_datetime": 1900000000000, "end_datetime": 1900000060000}]
logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_B_006_TC = dict(id="EDU_B_006", group="Authority Boundary", title="학습자 토큰으로 수업 일정 추가 차단", expected="_result fail (권한 없음)")


class TestCourseSectionScheduleAddBulkAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_006_TC)
    def test_course_edu_learner_cannot_add_section_schedule(self, learner_api_client, section_id):
        """[EDU_B_006] 학습자 토큰으로 교육자 전용 수업 일정 추가 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '수업 일정 추가(POST)' API를 호출하면
        _result fail(권한 없음)로 차단되어야 한다. (막히므로 실제로 일정이 추가되지 않음)"""
        logger.info("▶ [EDU_B_006] 학습자 수업 일정 추가 차단 검증 (course_section_id=%s)", section_id)
        resp = CourseEduPage(learner_api_client).add_section_schedules(course_section_id=section_id,
            section_schedule_list=_DUMMY_SCHEDULES,
        )
        assert_rest_result_failed(resp)

