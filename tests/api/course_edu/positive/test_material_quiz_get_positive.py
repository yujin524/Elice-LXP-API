# 퀴즈 수업자료 상세 조회 GET /org/{org}/material_quiz/get API 테스트 — EDU_010

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_010_TC = dict(id="EDU_010", group="Positive", title="퀴즈 수업자료 상세 조회", expected="_result ok, material_quiz 포함")


@pytest.mark.tc(**EDU_010_TC)
def test_material_quiz_detail(api_client, sandbox_quiz):
    """퀴즈 수업자료 상세 (org/material_quiz/get). 조회만 하므로 데이터 변경 없음."""
    material_quiz_id = sandbox_quiz["material_quiz_id"]
    logger.info("▶ [EDU_010] 퀴즈 상세 조회 시작 (material_quiz_id=%s)", material_quiz_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_material_quiz(material_quiz_id=material_quiz_id))
    quiz = body.get("material_quiz") or body
    assert "material_quiz" in body or "title" in quiz
    logger.info("  └ 퀴즈 제목: %s", quiz.get("title"))


