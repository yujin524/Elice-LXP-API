# 학생별 과목 학습현황 인증 GET /student/{id}/course (dashboard) API 테스트 — EDU_N_041

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_041_TC = dict(id="EDU_N_041", group="Authentication", title="학생별 과목 학습현황 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**EDU_N_041_TC)
@AuthNegativeCases.parametrize()
def test_student_course_progress_neg_auth(api_client_factory, student_user_id, classroom_id, client_kwargs):
    """[EDU_N_041] 학생별 과목 학습현황 - 인증 실패 거부
    내용 : 깨진 인증 client로 '학생별 과목 학습현황 조회(GET)' API를 호출하면
    401/403/409 중 하나로 거부되어야 한다. (dashboard 계열, HTTP 상태 판정)"""
    logger.info("▶ [EDU_N_041-neg] 학생별 과목 학습현황 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).get_student_course_progress(student_user_id=student_user_id, classroom_id=classroom_id)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "EDU_N_041 학생별 과목 학습현황 인증 실패")
