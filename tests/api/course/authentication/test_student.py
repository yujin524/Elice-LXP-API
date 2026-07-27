# 학습현황 요약 조회 GET /student/{student_user_id} API 테스트 — CO_N_004

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_004_TC = dict(id="CO_N_004", group="Authentication", title="학습현황 요약 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_004_TC)
@AuthNegativeCases.parametrize()
def test_learning_status_summary_neg_auth(api_client_factory, classroom_id, course_id, student_user_id, cohort_id, client_kwargs):
    """학습현황 요약 - 깨진 인증 client는 요약을 못 받아야 한다."""
    logger.info("▶ [CO_N_004-neg] 학습현황 요약 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_learning_status_summary(
        student_user_id=student_user_id, classroom_id=classroom_id, course_id=course_id, cohort_id=cohort_id
    )
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "CO_N_004 학습현황 요약 인증 실패")


