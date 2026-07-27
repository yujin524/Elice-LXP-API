# 다음 학습 위치 조회 GET /course/{course_id}/next_lecture_page API 테스트 — CO_N_002

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_002_TC = dict(id="CO_N_002", group="Authentication", title="다음 학습 위치 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_002_TC)
@AuthNegativeCases.parametrize()
def test_next_lecture_page_neg_auth(api_client_factory, course_id, client_kwargs):
    """다음 학습 위치 - 깨진 인증 client는 조회에 실패해야 한다."""
    logger.info("▶ [CO_N_002-neg] 다음 학습 위치 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_next_lecture_page(course_id=course_id)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "CO_N_002 다음 학습 위치 인증 실패")


