# 수료 현황 목록 조회 GET /org/course/completion/list API 테스트 — EDU_N_005

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_005_TC = dict(id="EDU_N_005", group="Authentication", title="수료 현황 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_005_TC)
@AuthNegativeCases.parametrize()
def test_completion_list_neg_auth(api_client_factory, client_kwargs):
    """수료 현황 - 깨진 인증 client는 목록을 못 받아야 한다. (조직 단위, course_id 불필요)"""
    logger.info("▶ [EDU_N_005-neg] 수료 현황 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    assert_rest_result_failed(CourseEduPage(client).get_completion_list())


