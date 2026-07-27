# 강의 목록 조회 GET /org/lecture/list API 테스트 — EDU_N_006

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_006_TC = dict(id="EDU_N_006", group="Authentication", title="강의 목록 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_006_TC)
@AuthNegativeCases.parametrize()
def test_lecture_list_neg_auth(api_client_factory, course_id, client_kwargs):
    """강의 목록 - 깨진 인증 client는 목록을 못 받아야 한다."""
    logger.info("▶ [EDU_N_006-neg] 강의 목록 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    assert_rest_result_failed(CourseEduPage(client).get_lecture_list(course_id=course_id))


