# 퀴즈 답안 제출 POST /org/{org_name}/material_quiz/response/add/ API 테스트 — CO_010

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_010_TC = dict(id="CO_010", group="Positive", title="퀴즈 답안 제출", expected="200")


@pytest.mark.tc(**CO_010_TC)
def test_quiz_submit(api_client, quiz_material_id):
    """퀴즈 답안 제출 (response/add/)."""
    logger.info("▶ [CO_010] 퀴즈 답안 제출 시작 (material_quiz_id=%s, answer=[3])", quiz_material_id)
    resp = CoursePage(api_client).quiz_submit(material_quiz_id=quiz_material_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_010 퀴즈 답안 제출")
    logger.info(f"  └ 퀴즈 제출 확인됨: material_quiz_id={quiz_material_id}, answer=[3]")



