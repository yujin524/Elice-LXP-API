# 클래스 학습현황 조회 GET /classroom/{classroom_id} API 테스트 — API_CH_002 ~ 004

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_response_status
from tests.api.common.params import INVALID_CLASSROOM_ID, NOT_FOUND_CLASSROOM_ID

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_002_TC = dict(id="API_CH_002", group="Validation - classroom_id", title="classroom_id 빈 값/누락", expected="HTTP 422")
API_CH_003_TC = dict(id="API_CH_003", group="Validation - classroom_id", title="존재하지 않는 classroom_id", expected="HTTP 409")
API_CH_004_TC = dict(id="API_CH_004", group="Validation - classroom_id", title="classroom_id 형식 오류", expected="HTTP 422")

CLASSROOM_ID_CASES = [
    pytest.param(
        "API_CH_002",
        None,
        422,
        "classroom_id 빈 값/누락",
        id="API_CH_002_classroom_id_missing",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(
                reason=(
                    "classroom_id 경로 조각 없이 /classroom/ 호출 시 422가 아니라 "
                    "read timeout으로 hang될 수 있음."
                )
            ),
            pytest.mark.tc(**API_CH_002_TC),
        ],
    ),
    pytest.param(
        "API_CH_003",
        NOT_FOUND_CLASSROOM_ID,
        409,
        "존재하지 않는 classroom_id",
        id="API_CH_003_classroom_id_not_found",
        marks=pytest.mark.tc(**API_CH_003_TC),
    ),
    pytest.param(
        "API_CH_004",
        INVALID_CLASSROOM_ID,
        422,
        "classroom_id 형식 오류",
        id="API_CH_004_classroom_id_invalid_format",
        marks=pytest.mark.tc(**API_CH_004_TC),
    ),
]


@pytest.mark.parametrize("tc_id, classroom_id_value, expected_status, title", CLASSROOM_ID_CASES)
def test_get_classroom_detail_classroom_id_validation(
    classroom_page,
    tc_id: str,
    classroom_id_value: str | None,
    expected_status: int,
    title: str,
) -> None:
    """classroom_id path 값의 누락, 미존재, 형식 오류를 검증한다."""
    response = classroom_page.get_classroom_detail(classroom_id_value)

    logger.info("[%s] %s 응답 status=%s", tc_id, title, response.status_code)
    assert_response_status(response, expected_status, f"{tc_id} | {title}")
