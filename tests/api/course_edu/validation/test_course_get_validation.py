# 과목 상세 조회 검증 GET /org/{org}/course/get API 테스트 — EDU_N_014, 025

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_014_TC = dict(id="EDU_N_014", group="Validation - Path Params", title="없는 course_id 과목 상세 조회", expected="_result fail")
EDU_N_025_TC = dict(id="EDU_N_025", group="Validation - Query Params", title="과목 상세 - course_id 타입 오류(문자열)", expected="_result fail")


@pytest.mark.tc(**EDU_N_014_TC)
def test_course_detail_nonexistent(api_client):
    logger.info("▶ [EDU_N_014] 없는 course_id 과목 상세 조회")
    assert_rest_result_failed(CourseEduPage(api_client).get_course_detail(course_id=NONEXISTENT_ID))


@pytest.mark.tc(**EDU_N_025_TC)
def test_course_detail_invalid_type(api_client):
    """course_id에 숫자가 아닌 문자열 -> 거부."""
    logger.info("▶ [EDU_N_025] course_id에 문자열 전달")
    assert_rest_result_failed(CourseEduPage(api_client).get_course_detail(course_id="not-a-number"))


