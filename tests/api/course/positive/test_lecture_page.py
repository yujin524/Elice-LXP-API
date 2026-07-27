# 학습 페이지 로드 GET /lecture_page API 테스트 — CO_003

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_003_TC = dict(id="CO_003", group="Positive", title="학습 페이지 로드", expected="200 + 콘텐츠 배열")


@pytest.mark.tc(**CO_003_TC)
def test_lecture_page_load(api_client, course_id, lecture_id):
    """학습 페이지 로드 - 200이고 콘텐츠 배열에 필수 필드가 있어야 한다."""
    logger.info("▶ [CO_003] 학습 페이지 로드 시작 (course_id=%s, lecture_id=%s)", course_id, lecture_id)
    resp = CoursePage(api_client).get_lecture_page_list(course_id=course_id, lecture_id=lecture_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_003 학습 페이지 로드")

    body = resp.json()
    assert isinstance(body, list)
    logger.info("  └ lecture_page %d개 콘텐츠 조회됨", len(body))

    if body:
        first = body[0]
        assert "title" in first
        assert "material_type" in first
        logger.info("  └ 필수 필드(title, material_type) 확인 완료")



