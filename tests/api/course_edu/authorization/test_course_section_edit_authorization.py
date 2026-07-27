# 섹션 편집 POST /org/course/section/edit API 테스트 — EDU_B_009

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

EDU_B_004_TC = dict(id="EDU_B_004", group="Authority Boundary", title="학습자 토큰으로 섹션 편집 차단", expected="_result fail (권한 없음)")


class TestCourseSectionEditAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_004_TC)
    def test_course_edu_learner_cannot_edit_section(self, learner_api_client, course_id, section_id):
        """[EDU_B_004] 학습자 토큰으로 교육자 전용 섹션 편집 차단
        내용 : 학습자(le01) 권한으로 교육자 전용인 '섹션 편집(POST)' API를 호출하면
        _result fail(권한 없음)로 차단되어야 한다. (막히므로 실제로 바뀌지 않음)"""
        logger.info("▶ [EDU_B_004] 학습자 섹션 편집 차단 검증 (section_id=%s)", section_id)
        resp = CourseEduPage(learner_api_client).edit_section(course_id=course_id,
            name="권한없는_학습자_섹션편집_시도",
            course_section_id=section_id,
        )
        assert_rest_result_failed(resp)

