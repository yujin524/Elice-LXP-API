# 수강 후기 목록 조회 검증 GET /org/{org}/course/info/review/list API 테스트 — EDU_N_020

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_020_TC = dict(id="EDU_N_020", group="Validation - Path Params", title="없는 course_info_id 후기 목록 조회", expected="_result fail")


@pytest.mark.tc(**EDU_N_020_TC)
def test_info_review_list_nonexistent(api_client):
    logger.info("▶ [EDU_N_020] 없는 course_info_id 수강 후기 목록 조회")
    assert_rest_result_failed(CourseEduPage(api_client).get_info_review_list(course_info_id=NONEXISTENT_ID))


