# 섹션 이름 편집 후 복원 POST /org/{org}/course/section/edit API 테스트 — EDU_015

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_015_TC = dict(id="EDU_015", group="Positive", title="섹션 이름 편집 후 복원", expected="편집 반영 확인 후 원복")


def _section_name(api_client, course_id: int, section_id: int) -> str | None:
    """섹션 목록에서 해당 섹션의 현재 이름을 읽는다."""
    sections = CourseEduPage(api_client).get_section_list(course_id=course_id, offset=0, count=20).json().get("course_sections", [])
    sec = next((s for s in sections if (s.get("id") or s.get("course_section_id")) == section_id), {})
    return sec.get("name")


@pytest.mark.tc(**EDU_015_TC)
def test_section_edit_and_restore(api_client, course_id, section_id):
    """섹션 이름을 잠깐 바꿔 반영을 확인하고, 반드시 원래 값으로 되돌린다."""
    original_name = _section_name(api_client, course_id, section_id)
    if original_name is None:
        pytest.skip("섹션 이름을 찾지 못했습니다.")
    new_name = f"{original_name} [QA-EDIT]"

    logger.info("▶ [EDU_015] 섹션 편집-복원 시작 (course_id=%s, section_id=%s, orig=%r)",
                course_id, section_id, original_name)
    try:
        assert_rest_result_ok(CourseEduPage(api_client).edit_section(course_id=course_id, name=new_name, course_section_id=section_id))
        assert _section_name(api_client, course_id, section_id) == new_name
        logger.info("  └ 이름 변경 반영 확인: %r", new_name)
    finally:
        assert_rest_result_ok(CourseEduPage(api_client).edit_section(course_id=course_id, name=original_name, course_section_id=section_id))
        assert _section_name(api_client, course_id, section_id) == original_name
        logger.info("  └ 원복 완료: %r", original_name)


