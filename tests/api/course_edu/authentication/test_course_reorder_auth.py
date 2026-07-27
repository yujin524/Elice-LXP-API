# 클래스룸 과목 순서 변경 POST /classroom/{classroom_id}/course/reorder API 테스트 — EDU_N_013

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_013_TC = dict(id="EDU_N_013", group="Authentication", title="과목 순서 변경 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**EDU_N_013_TC)
@AuthNegativeCases.parametrize()
def test_course_reorder_neg_auth(api_client, api_client_factory, classroom_id, client_kwargs):
    """과목 순서 변경 - 깨진 인증 client는 순서 변경에 실패해야 한다(순서 변경 없음)."""
    # 정상 client로 현재 순서를 읽어, 깨진 client에는 동일 순서(no-op)를 보낸다.
    # (reorder는 전체 course_id 집합과 정확히 일치해야 하므로 페이징 끝까지 모은다)
    courses = CourseEduPage(api_client).list_all_classroom_courses(classroom_id=classroom_id)
    current_order = [c["course_id"] for c in courses]

    logger.info("▶ [EDU_N_013-neg] 과목 순서 변경 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).reorder_courses(classroom_id=classroom_id, course_ids=current_order)
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert_response_status(resp, AuthNegativeCases.STATUS_CODES, "EDU_N_013 과목 순서 변경 인증 실패")


