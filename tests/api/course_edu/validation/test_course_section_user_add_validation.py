# 섹션 수강생 추가 검증 POST /org/{org}/course/section/user/add/by_user_ident API 테스트 — EDU_N_038

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_038_TC = dict(id="EDU_N_038", group="Validation - Query Params", title="수강생 추가 - 없는 course_section_id", expected="_result fail")



@pytest.mark.tc(**EDU_N_038_TC)
def test_add_section_users_nonexistent_section(api_client):
    """없는 course_section_id로 수강생 추가 시도 -> 거부 (대상이 없어 아무것도 안 바뀜)."""
    logger.info("▶ [EDU_N_038] 없는 course_section_id=%s 로 수강생 추가 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).add_section_users(course_section_id=NONEXISTENT_ID,
        user_ident_list=["qa_validation_nobody@example.com"],
    )
    assert_rest_result_failed(resp)


