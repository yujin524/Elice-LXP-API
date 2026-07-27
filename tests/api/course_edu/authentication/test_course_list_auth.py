# 교육자 과목 목록 인증 GET /org/{org}/course/list API 테스트 — EDU_N_039

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_039_TC = dict(id="EDU_N_039", group="Authentication", title="과목 목록 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_039_TC)
@AuthNegativeCases.parametrize()
def test_course_list_neg_auth(api_client_factory, client_kwargs):
    """[EDU_N_039] 과목 목록 - 인증 실패 거부
    내용 : 깨진 인증 client(토큰 없음/빈 값/공백/잘못된 값)로 '과목 목록 조회(GET)' API를
    호출하면 _result fail로 거부되어야 한다."""
    logger.info("▶ [EDU_N_039-neg] 과목 목록 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    assert_rest_result_failed(CourseEduPage(client).get_course_list())
