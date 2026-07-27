# 학습 종료 GET /course/{course_id}/curriculum API 테스트 — CO_013

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_013_TC = dict(id="CO_013", group="Positive", title="학습 종료", expected="200")


@pytest.mark.tc(**CO_013_TC)
def test_course_exit(api_client, course_id):
    """
    학습 종료 - 학습 화면에서 '나가기' 시 호출되는 API로 종료 처리를 확인한다 (/course/{id}/curriculum).

    학습을 종료하고 과목 상세로 복귀할 때 이 커리큘럼 API가 호출되며,
    200이면 학습 종료가 정상 처리된 것으로 본다.
    """
    logger.info("▶ [CO_013] 학습 종료 API 호출 시작 (course_id=%s)", course_id)
    resp = CoursePage(api_client).get_curriculum(course_id=course_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_013 학습 종료")
    logger.info("  └ 학습 종료 정상 처리 확인됨")



