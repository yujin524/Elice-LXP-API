# 과목소개 페이지 로딩 GET /courses/{course_id} API 테스트 — CO_008

import logging
import pytest
import requests
from tests.api.common.params import course_intro_params
from config import settings
from utils.logger import log_direct_request, log_direct_response
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_008_TC = dict(id="CO_008", group="Positive", title="과목소개 페이지 로딩", expected="200")


@pytest.mark.tc(**CO_008_TC)
def test_course_intro_page_load(course_id):
    """
    '과목소개' 탭 - 페이지 로딩 확인.

    course-content-builder-viewer.app.elice.io는 React SPA 껍데기만 반환하고
    4개 주력 도메인 밖의 별도 마이크로서비스라, 페이지 로딩(200) 여부만 확인한다.
    실제 본문 텍스트 검증은 CO_006의 응답으로 대신한다.

    주의: 이 도메인은 Bearer 토큰을 보내면 Azure 인증 방식과 충돌하므로 인증 없이 호출한다.
    """
    logger.info("▶ [CO_008] 과목소개 페이지 로딩 확인 시작 (course_id=%s)", course_id)
    url = f"https://course-content-builder-viewer.app.elice.io/courses/{course_id}"
    params = course_intro_params(settings.ELICE_ORG_NAME_SHORT)
    log_direct_request(logger, "GET", url, params=params)
    resp = requests.get(url, params=params, timeout=settings.API_TIMEOUT_SECONDS)
    log_direct_response(logger, resp)

    logger.info(f"  └ 응답 수신: status={resp.status_code}, 크기={len(resp.content)} bytes")
    assert_response_status(resp, 200, "CO_008 과목소개 페이지 로딩")



