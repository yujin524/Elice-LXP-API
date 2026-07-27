# 수업 제목 편집 후 복원 POST /org/{org}/lecture/edit API 테스트 — EDU_011

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_011_TC = dict(id="EDU_011", group="Positive", title="수업 제목 편집 후 복원", expected="편집 반영 확인 후 원복")


def _current_title(api_client, course_id: int, lecture_id: int) -> str | None:
    """lecture 목록에서 해당 수업의 현재 제목을 읽는다."""
    lectures = CourseEduPage(api_client).get_lecture_list(course_id=course_id, offset=0, count=30).json().get("lectures", [])
    lecture = next((x for x in lectures if (x.get("id") or x.get("lecture_id")) == lecture_id), {})
    return lecture.get("title")


@pytest.mark.tc(**EDU_011_TC)
def test_lecture_edit_and_restore(api_client, editable_lecture):
    """수업 제목을 잠깐 바꿔 반영을 확인하고, 반드시 원래 값으로 되돌린다."""
    course_id, lecture = editable_lecture
    lecture_id = lecture.get("id") or lecture.get("lecture_id")
    original_title = lecture.get("title")
    new_title = f"{original_title} [QA-EDIT]"

    # 편집 시 필수 필드(현재 값 보존)
    common = dict(
        course_id=course_id,
        lecture_id=lecture_id,
        lecture_type=lecture.get("lecture_type", 0),
        description=lecture.get("description") or "",
        is_opened=bool(lecture.get("is_opened")),
        is_preview=bool(lecture.get("is_preview")),
    )

    logger.info("▶ [EDU_011] 수업 편집-복원 시작 (course_id=%s, lecture_id=%s, orig=%r)",
                course_id, lecture_id, original_title)
    try:
        # 1) 제목 변경
        assert_rest_result_ok(CourseEduPage(api_client).edit_lecture(title=new_title, **common))
        # 2) 반영 확인
        assert _current_title(api_client, course_id, lecture_id) == new_title
        logger.info("  └ 제목 변경 반영 확인: %r", new_title)
    finally:
        # 3) 원복 (앞 단계가 실패해도 반드시 복원)
        assert_rest_result_ok(CourseEduPage(api_client).edit_lecture(title=original_title, **common))
        assert _current_title(api_client, course_id, lecture_id) == original_title
        logger.info("  └ 원복 완료: %r", original_title)


