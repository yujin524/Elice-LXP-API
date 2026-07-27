# 퀴즈 문제 진입 POST /org/{org_name}/material_quiz/options_set/select/ API 테스트 — CO_N_009

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_009_TC = dict(id="CO_N_009", group="Authentication", title="퀴즈 진입 - 인증 실패 거부", expected="_result.status=fail")


@pytest.mark.tc(**CO_N_009_TC)
@AuthNegativeCases.parametrize()
def test_quiz_enter_neg_auth(api_client_factory, quiz_material_id, client_kwargs):
    """퀴즈 진입 - 깨진 인증 client는 진입에 실패해야 한다.

    REST 계열이라 HTTP는 200을 주고 body의 _result로 실패를 확인한다.
    """
    logger.info("▶ [CO_N_009-neg] 퀴즈 진입 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).quiz_enter(material_quiz_id=quiz_material_id)
    logger.info("  └ HTTP status=%s (REST 계열: body의 _result로 판정)", resp.status_code)
    assert_rest_result_failed(resp)


