# 퀴즈 수업자료 상세 조회 검증 GET /org/{org}/material_quiz/get API 테스트 — EDU_N_016

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_016_TC = dict(id="EDU_N_016", group="Validation - Path Params", title="없는 퀴즈 id 상세 조회", expected="_result fail")


@pytest.mark.tc(**EDU_N_016_TC)
def test_material_quiz_nonexistent(api_client):
    logger.info("▶ [EDU_N_016] 없는 material_quiz_id 상세 조회")
    assert_rest_result_failed(CourseEduPage(api_client).get_material_quiz(material_quiz_id=NONEXISTENT_ID))


