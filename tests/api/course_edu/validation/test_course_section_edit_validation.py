# 섹션 편집 검증 POST /org/{org}/course/section/edit API 테스트 — EDU_N_037

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_037_TC = dict(id="EDU_N_037", group="Validation - Query Params", title="섹션 편집 - 없는 course_id", expected="_result fail")



@pytest.mark.tc(**EDU_N_037_TC)
def test_section_edit_nonexistent_course(api_client):
    """없는 course_id로 섹션 편집/생성 시도 -> 거부 (대상이 없어 아무것도 안 만들어짐)."""
    logger.info("▶ [EDU_N_037] 없는 course_id=%s 로 섹션 편집 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).edit_section(course_id=NONEXISTENT_ID, name="검증용_없는과목_섹션")
    assert_rest_result_failed(resp)


