# 과제 자료 편집 검증 POST /org/{org}/material_assignment/edit API 테스트 — EDU_N_028

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_028_TC = dict(id="EDU_N_028", group="Validation - Query Params", title="과제 편집 - 없는 lecture_id", expected="_result fail")


@pytest.mark.tc(**EDU_N_028_TC)
def test_edit_assignment_nonexistent_lecture(api_client):
    """없는 lecture_id로 과제 편집 -> 거부 (대상이 없어 아무것도 안 만들어짐)."""
    logger.info("▶ [EDU_N_028] 없는 lecture_id=%s 로 과제 편집 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).edit_material_assignment(lecture_id=NONEXISTENT_ID,
        title="검증용_없는수업_과제편집",
    )
    assert_rest_result_failed(resp)


