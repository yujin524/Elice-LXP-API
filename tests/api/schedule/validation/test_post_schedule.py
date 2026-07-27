# 수업 일정 등록 POST /schedule API 테스트 — API_CS_026 ~ 028

import logging
import pytest
from tests.api.common.assertions import format_error_detail
from tests.api.common.payload import schedule_create_payload


logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CS_026_TC = dict(id="API_CS_026", group="Validation", title="classroom_id 누락", expected="HTTP 422, classroom_id 필수값 누락 오류")
API_CS_027_TC = dict(id="API_CS_027", group="Validation", title="summary 누락", expected="HTTP 422, summary 필수값 누락 오류")
API_CS_028_TC = dict(id="API_CS_028", group="Validation", title="dt_end 누락", expected="HTTP 422, dt_end 필수값 누락 오류")


@pytest.mark.parametrize(
    "tc_id, missing_field",
    [
        pytest.param(
            "API_CS_026",
            "classroom_id",
            marks=pytest.mark.tc(**API_CS_026_TC),
            id="API_CS_026",
        ),
        pytest.param(
            "API_CS_027",
            "summary",
            marks=pytest.mark.tc(**API_CS_027_TC),
            id="API_CS_027",
        ),
        pytest.param(
            "API_CS_028",
            "dt_end",
            marks=pytest.mark.tc(**API_CS_028_TC),
            id="API_CS_028",
        ),
    ],
)
def test_educator_cannot_create_schedule_without_required_body_field(schedule_post_page, classroom_id, tc_id, missing_field,):
    """[API_CS_026~028] 필수 Body field 누락
    내용 : 교육자 계정으로 '수업 일정 등록(POST)' API를 필수 Body field 없이 호출하면
    422 Unprocessable Entity와 함께 missing 오류가 반환되어야 한다."""
    logger.info("[%s] 수업 일정 등록 필수값 누락 요청: %s", tc_id, missing_field)

    payload = schedule_create_payload(classroom_id, **{missing_field: None},)

    response = schedule_post_page.create_schedule(**payload)

    logger.info("수업 일정 등록 필수값 누락 응답 status=%s", response.status_code)
    logger.debug("수업 일정 등록 필수값 누락 응답 body=%s", response.text)

    assert response.status_code == 422, (
        f"{missing_field} 누락이 걸러지지 않음! "
        f"상태 코드: {response.status_code}, 응답: {response.text}"
    )

    body = response.json()
    detail = body["detail"][0]

    assert detail["type"] == "missing", f"예상과 다른 오류 타입: {detail!r}"
    assert "body" in detail["loc"], f"Body 필드를 가리키지 않음: {detail!r}"
    assert missing_field in detail["loc"], f"{missing_field} 필드를 가리키지 않음: {detail!r}"
    assert detail["msg"] == "Field required", f"예상과 다른 오류 메시지: {detail!r}"

    logger.info("%s 누락 검증 결과: %s", missing_field, format_error_detail(detail))
