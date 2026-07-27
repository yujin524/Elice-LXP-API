# 강의실 상세 조회 GET /org/{org}/course/lectureroom/get/ API 테스트 — API_CS_022

import logging
import pytest
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import lectureroom_detail_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_022_TC = dict(id="API_CS_022", group="Validation", title="lectureroom_id 누락", expected="HTTP 400")


@pytest.mark.xfail(
    reason="lectureroom_id 누락 시 HTTP 400이 기대되지만, 현재 API는 HTTP 200 + Body 내부 status_code=400으로 반환됨",
    strict=True,
)
@pytest.mark.tc(**API_CS_022_TC)
def test_learner_cannot_get_lectureroom_detail_without_lectureroom_id(
    lectureroom_page,
    api_settings,
):
    """[API_CS_022] lectureroom_id 누락
    내용 : 학습자(qatrack) 계정으로 '강의실 상세 조회(GET)' API를 lectureroom_id 없이
    호출하면 HTTP 400 Bad Request가 반환되어야 한다."""
    logger.info("[API_CS_022] lectureroom_id 누락 상태로 강의실 상세 조회 요청")

    response = lectureroom_page.get_lectureroom(
        org=api_settings.ELICE_ORG_NAME_SHORT,
        **lectureroom_detail_params(None),
    )

    logger.info("lectureroom_id 누락 응답 status=%s", response.status_code)
    logger.debug("lectureroom_id 누락 응답 body=%s", response.text)

    assert_response_status(response, 400, "API_CS_022 | lectureroom_id 누락")
