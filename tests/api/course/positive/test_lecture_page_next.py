# 다음 강의자료 확인 GET /lecture_page/{material_id}/next API 테스트 — CO_011

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_011_TC = dict(id="CO_011", group="Positive", title="다음 강의자료 확인", expected="200")


@pytest.mark.tc(**CO_011_TC)
def test_next_lecture_material(api_client, course_id, quiz_material_id):
    """다음 강의자료 존재 여부 확인 (/lecture_page/{id}/next)."""
    logger.info("▶ [CO_011] 다음 강의자료 확인 시작 (material_id=%s)", quiz_material_id)
    resp = CoursePage(api_client).get_next_material(material_id=quiz_material_id, course_id=course_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_011 다음 강의자료 확인")
    logger.info(f"  └ 다음 강의자료 확인 응답: {resp.text[:200]}")



