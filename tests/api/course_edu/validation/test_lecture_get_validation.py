# 강의 상세 조회 검증 GET /org/{org}/lecture/get API 테스트 — EDU_N_019

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_019_TC = dict(id="EDU_N_019", group="Validation - Path Params", title="없는 lecture 상세 조회", expected="_result fail")


@pytest.mark.tc(**EDU_N_019_TC)
def test_lecture_detail_nonexistent(api_client):
    logger.info("▶ [EDU_N_019] 없는 lecture_id/section_id 강의 상세 조회")
    resp = CourseEduPage(api_client).get_lecture_detail(lecture_id=NONEXISTENT_ID, course_section_id=NONEXISTENT_ID)
    assert_rest_result_failed(resp)


