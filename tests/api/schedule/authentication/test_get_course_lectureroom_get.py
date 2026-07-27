# 강의실 상세 조회 GET /org/{org}/course/lectureroom/get/ API 테스트 — API_CS_023

import logging
import pytest
from apis.schedule_api.schedule import LectureroomPage
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import lectureroom_detail_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_023_TC = dict(id="API_CS_023", group="Authentication", title="Authorization 헤더 누락", expected="HTTP 403")


@pytest.mark.xfail(
    reason="Authorization 누락 시 HTTP 403이 기대되지만, 현재 API는 HTTP 200 + Body 내부 status_code=403으로 반환됨",
    strict=True,
)
@pytest.mark.tc(**API_CS_023_TC)
def test_learner_cannot_get_lectureroom_detail_without_authorization(
    api_client_factory,
    api_settings,
    lectureroom_id,
):
    """[API_CS_023] Authorization 헤더 누락
    내용 : 학습자(qatrack) 계정으로 '강의실 상세 조회(GET)' API를 Authorization 헤더 없이
    호출하면 HTTP 403 Forbidden이 반환되어야 한다."""
    logger.info("[API_CS_023] Authorization 헤더 없이 강의실 상세 조회 요청")

    client = api_client_factory(include_auth=False)
    response = LectureroomPage(client).get_lectureroom(
        org=api_settings.ELICE_ORG_NAME_SHORT,
        **lectureroom_detail_params(lectureroom_id),
    )

    logger.info("lectureroom 인증 실패 응답 status=%s", response.status_code)
    logger.debug("lectureroom 인증 실패 응답 body=%s", response.text)

    assert_response_status(response, 403, "API_CS_023 | Authorization 헤더 누락")
