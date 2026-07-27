# 강의 상세 조회 GET /org/lecture/get API 테스트 — EDU_N_009

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_009_TC = dict(id="EDU_N_009", group="Authentication", title="강의 상세 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_009_TC)
@AuthNegativeCases.parametrize()
def test_lecture_detail_neg_auth(api_client_factory, lecture_id, section_id, client_kwargs):
    """강의 상세 - 깨진 인증 client는 상세를 못 받아야 한다."""
    logger.info("▶ [EDU_N_009-neg] 강의 상세 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    assert_rest_result_failed(CourseEduPage(client).get_lecture_detail(lecture_id=lecture_id, course_section_id=section_id))


