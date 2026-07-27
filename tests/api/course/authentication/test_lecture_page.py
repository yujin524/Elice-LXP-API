# 학습 페이지 로드 GET /lecture_page API 테스트 — CO_N_003

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_003_TC = dict(id="CO_N_003", group="Authentication", title="학습 페이지 로드 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_003_TC)
@AuthNegativeCases.parametrize()
def test_lecture_page_load_neg_auth(api_client_factory, course_id, lecture_id, client_kwargs):
    """학습 페이지 로드 - 깨진 인증 client는 콘텐츠를 못 받아야 한다."""
    logger.info("▶ [CO_N_003-neg] 학습 페이지 로드 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_lecture_page_list(course_id=course_id, lecture_id=lecture_id)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "CO_N_003 학습 페이지 로드 인증 실패")


