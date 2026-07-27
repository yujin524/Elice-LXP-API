# 퀴즈 편집 POST /org/material_quiz/edit API 테스트 — EDU_B_002

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_B_003_TC = dict(id="EDU_B_003", group="Authority Boundary", title="학습자 토큰으로 퀴즈 자료 편집 차단", expected="_result fail (권한 없음)")


class TestMaterialQuizEditAuthorityBoundary:

    @pytest.mark.tc(**EDU_B_003_TC)
    def test_course_edu_learner_cannot_edit_material_quiz(self, learner_api_client, sandbox_quiz):
        """[EDU_B_003] 학습자 토큰으로 교육자 전용 퀴즈 자료 편집 차단
        내용 : 학습자(le05) 권한으로 교육자 전용인 '퀴즈 자료 편집(POST)' API를 호출하면
        _result fail(권한 없음)로 차단되어야 한다."""
        logger.info("▶ [EDU_B_003] 학습자 퀴즈 편집 차단 검증 (material_quiz_id=%s)",
                    sandbox_quiz["material_quiz_id"])
        resp = CourseEduPage(learner_api_client).edit_material_quiz(material_quiz_id=sandbox_quiz["material_quiz_id"],
            lecture_id=sandbox_quiz["lecture_id"],
            lecture_page_id=sandbox_quiz["lecture_page_id"],
            title="QA boundary-neg",
        )
        assert_rest_result_failed(resp)

