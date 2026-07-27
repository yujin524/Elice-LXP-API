# 강의실 상세 조회 GET /org/{org}/course/lectureroom/get/ API 테스트 — API_CS_021

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_ok
from tests.api.common.params import lectureroom_detail_params

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_021_TC = dict(id="API_CS_021", group="Positive", title="강의실 상세 정보 정상 조회", expected="HTTP 200")


@pytest.mark.tc(**API_CS_021_TC)
def test_learner_can_get_lectureroom_detail(
    lectureroom_page,
    api_settings,
    lectureroom_id,
):
    """[API_CS_021] 강의실 상세 정보 정상 조회
    내용 : 학습자(qatrack) 계정으로 '강의실 상세 조회(GET)' API를 유효한 lectureroom_id로
    호출하면 200 OK와 함께 강의실 상세 정보가 반환되어야 한다."""
    logger.info("[API_CS_021] 강의실 상세 정보 정상 조회 요청")

    response = lectureroom_page.get_lectureroom(
        org=api_settings.ELICE_ORG_NAME_SHORT,
        **lectureroom_detail_params(lectureroom_id),
    )

    logger.info("lectureroom 상세 조회 응답 status=%s", response.status_code)

    body = assert_rest_result_ok(response)

    assert body, f"응답 Body가 비어 있음: {body!r}"

    logger.debug("lectureroom 상세 조회 결과: %s", body)
