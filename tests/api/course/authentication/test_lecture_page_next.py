# 다음 강의자료 확인 GET /lecture_page/{material_id}/next API 테스트 — CO_N_011

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_011_TC = dict(id="CO_N_011", group="Authentication", title="다음 강의자료 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_011_TC)
@AuthNegativeCases.parametrize()
def test_next_lecture_material_neg_auth(api_client_factory, course_id, quiz_material_id, client_kwargs):
    """다음 강의자료 - 깨진 인증 client는 확인에 실패해야 한다."""
    logger.info("▶ [CO_N_011-neg] 다음 강의자료 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_next_material(material_id=quiz_material_id, course_id=course_id)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "CO_N_011 다음 강의자료 인증 실패")


