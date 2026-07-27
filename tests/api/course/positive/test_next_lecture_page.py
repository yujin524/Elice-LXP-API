# 다음 학습 위치 조회 GET /course/{course_id}/next_lecture_page API 테스트 — CO_002

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_002_TC = dict(id="CO_002", group="Positive", title="다음 학습 위치 조회", expected="200")


@pytest.mark.tc(**CO_002_TC)
def test_next_lecture_page(api_client, course_id):
    """학습 페이지 이동(다음 학습 위치 조회) - 200이어야 한다."""
    logger.info("▶ [CO_002] 다음 학습 위치 조회 시작 (course_id=%s)", course_id)
    resp = CoursePage(api_client).get_next_lecture_page(course_id=course_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_002 다음 학습 위치 조회")
    body = resp.json()
    # lecture_id는 null일 수 있음(과목 완료 시). 응답 구조에 키가 있는지만 확인.
    assert "lecture_id" in body
    logger.info("  └ next_lecture_page 응답: lecture_id=%s", body.get("lecture_id"))



