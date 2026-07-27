# 퀴즈 자료 제목 편집 후 복원 POST /org/{org}/material_quiz/edit API 테스트 — EDU_012

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_012_TC = dict(id="EDU_012", group="Positive", title="퀴즈 자료 제목 편집 후 복원(SANDBOX)", expected="편집 반영 확인 후 제목 원복")


def _quiz_title(api_client, material_quiz_id: int) -> str | None:
    """material_quiz/get에서 현재 퀴즈 제목을 읽는다."""
    body = assert_rest_result_ok(CourseEduPage(api_client).get_material_quiz(material_quiz_id=material_quiz_id))
    quiz = body.get("material_quiz") or body
    return quiz.get("title")


@pytest.mark.tc(**EDU_012_TC)
def test_material_quiz_edit_and_restore(api_client, sandbox_quiz):
    """SANDBOX 퀴즈의 제목을 잠깐 바꿔 반영을 확인하고, 제목을 원래 값으로 되돌린다.

    주의: 퀴즈 편집 payload는 문항 내용까지 포함하므로(고정 템플릿), title 외 내용은
    템플릿 값으로 정규화된다. 그래서 실제 과목이 아닌 **SANDBOX 전용**이다.
    """
    qid = sandbox_quiz["material_quiz_id"]
    original_title = _quiz_title(api_client, qid)
    new_title = f"{original_title} [QA-EDIT]"
    common = dict(
        material_quiz_id=qid,
        lecture_id=sandbox_quiz["lecture_id"],
        lecture_page_id=sandbox_quiz["lecture_page_id"],
    )

    logger.info("▶ [EDU_012] 퀴즈 편집-복원 시작 (material_quiz_id=%s, orig=%r)", qid, original_title)
    try:
        assert_rest_result_ok(CourseEduPage(api_client).edit_material_quiz(title=new_title, **common))
        assert _quiz_title(api_client, qid) == new_title
        logger.info("  └ 제목 변경 반영 확인: %r", new_title)
    finally:
        assert_rest_result_ok(CourseEduPage(api_client).edit_material_quiz(title=original_title, **common))
        assert _quiz_title(api_client, qid) == original_title
        logger.info("  └ 제목 원복 완료: %r", original_title)


