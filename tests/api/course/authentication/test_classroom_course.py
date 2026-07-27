# 학습 과목 목록 조회 GET /classroom/{classroom_id}/course API 테스트 — CO_N_001

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_001_TC = dict(id="CO_N_001", group="Authentication", title="과목 목록 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_001_TC)
@AuthNegativeCases.parametrize()
def test_course_list_neg_auth(api_client_factory, classroom_id, client_kwargs):
    """과목 목록 - 깨진 인증 client는 목록을 못 받아야 한다."""
    logger.info("▶ [CO_N_001-neg] 과목 목록 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_course_list(classroom_id=classroom_id)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "CO_N_001 과목 목록 인증 실패")


