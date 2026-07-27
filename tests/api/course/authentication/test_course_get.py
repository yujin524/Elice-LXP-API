# 학습맵(과목 상세) 조회 GET /org/{org_name}/course/get/ API 테스트 — CO_N_006

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_006_TC = dict(id="CO_N_006", group="Authentication", title="학습맵(과목 상세) - 인증 실패 거부", expected="_result.status=fail")


@pytest.mark.tc(**CO_N_006_TC)
@AuthNegativeCases.parametrize()
def test_course_detail_neg_auth(api_client_factory, course_id, client_kwargs):
    """학습맵(과목 상세) - 깨진 인증 client는 상세를 못 받아야 한다.

    REST 계열이라 HTTP는 200을 주고 body의 _result로 실패를 확인한다.
    """
    logger.info("▶ [CO_N_006-neg] 학습맵(과목 상세) 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_course_detail(course_id=course_id)
    logger.info("  └ HTTP status=%s (REST 계열: body의 _result로 판정)", resp.status_code)
    assert_rest_result_failed(resp)


