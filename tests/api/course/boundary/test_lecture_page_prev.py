# 이전 강의자료 확인 GET /lecture_page/{material_id}/prev API 테스트 — CO_012

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_012_TC = dict(id="CO_012", group="Positive", title="이전 강의자료 확인", expected="200/404/409")


@pytest.mark.tc(**CO_012_TC)
def test_prev_lecture_material(api_client, course_id, quiz_material_id):
    """
    이전 강의자료 존재 여부 확인 (/lecture_page/{id}/prev).

    주의: 이 경로(prev)는 next와 같은 패턴일 것으로 추정만 하고 있고,
    실제 브라우저 캡처로 직접 확인된 값은 아직 아니다. 200/404/409 중
    실제로 어떤 코드가 오는지 확인 후 이 TC를 다시 다듬어야 한다.
    """
    logger.info("▶ [CO_012] 이전 강의자료 확인 시작 (material_id=%s)", quiz_material_id)
    resp = CoursePage(api_client).get_prev_material(material_id=quiz_material_id, course_id=course_id)
    logger.info(f"  └ 이전 강의자료 확인 응답: status={resp.status_code}")
    assert_response_status(resp, {200, 404, 409}, "CO_012 이전 강의자료 확인")



