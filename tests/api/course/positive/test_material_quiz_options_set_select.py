# 퀴즈 문제 진입 POST /org/{org_name}/material_quiz/options_set/select/ API 테스트 — CO_009

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_009_TC = dict(id="CO_009", group="Positive", title="퀴즈 문제 진입", expected="200")


@pytest.mark.tc(**CO_009_TC)
def test_quiz_enter(api_client, quiz_material_id):
    """퀴즈 문제 진입 (options_set/select/)."""
    logger.info("▶ [CO_009] 퀴즈 문제 진입 시작 (material_quiz_id=%s)", quiz_material_id)
    resp = CoursePage(api_client).quiz_enter(material_quiz_id=quiz_material_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_009 퀴즈 문제 진입")
    logger.info(f"  └ 퀴즈 진입 확인됨: material_quiz_id={quiz_material_id}")



