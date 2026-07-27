# 퀴즈 상세 조회 GET /org/material_quiz/get API 테스트 — EDU_N_010

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_010_TC = dict(id="EDU_N_010", group="Authentication", title="퀴즈 상세 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_010_TC)
@AuthNegativeCases.parametrize()
def test_material_quiz_detail_neg_auth(api_client_factory, sandbox_quiz, client_kwargs):
    """퀴즈 상세 - 깨진 인증 client는 상세를 못 받아야 한다."""
    logger.info("▶ [EDU_N_010-neg] 퀴즈 상세 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    assert_rest_result_failed(CourseEduPage(client).get_material_quiz(material_quiz_id=sandbox_quiz["material_quiz_id"]))


