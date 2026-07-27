# 라이브 강의실 생성 검증 POST /org/{org}/course/lectureroom/edit API 테스트 — EDU_N_027

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_027_TC = dict(id="EDU_N_027", group="Validation - Query Params", title="라이브 강의실 생성 - 없는 course_id", expected="_result fail")


@pytest.mark.tc(**EDU_N_027_TC)
def test_create_lectureroom_nonexistent_course(api_client):
    """없는 course_id/section으로 라이브 강의실 생성 -> 거부 (대상이 없어 아무것도 안 만들어짐)."""
    logger.info("▶ [EDU_N_027] 없는 course_id=%s 로 라이브 강의실 생성 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).create_lectureroom(course_id=NONEXISTENT_ID,
        course_section_id=NONEXISTENT_ID,
        title="검증용_없는과목_강의실생성",
    )
    assert_rest_result_failed(resp)


