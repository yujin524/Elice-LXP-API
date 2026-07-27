# 학습 과목 목록 조회 GET /classroom/{classroom_id}/course API 테스트 — CO_001

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_course_list

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_001_TC = dict(id="CO_001", group="Positive", title="학습 과목 목록 조회", expected="200 + 배열")


@pytest.mark.tc(**CO_001_TC)
def test_course_list(api_client, classroom_id):
    """학습 과목 목록 조회 - 200이고 배열이며 필수 필드가 있어야 한다."""
    logger.info("▶ [CO_001] 학습 과목 목록 조회 시작 (classroom_id=%s)", classroom_id)
    resp = CoursePage(api_client).get_course_list(classroom_id=classroom_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)

    body = assert_course_list(resp)
    logger.info("  └ 과목 %d개 조회됨", len(body))



