# 클래스 학습현황 조회 GET /classroom/{classroom_id} API 테스트 — API_CH_001, 008

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_classroom_detail

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_001_TC = dict(id="API_CH_001", group="Positive", title="정상 classroom_id로 조회", expected="HTTP 200")
API_CH_008_TC = dict(id="API_CH_008", group="Positive", title="학습현황 수치 정확성", expected="HTTP 200")

CLASSROOM_DETAIL_SUCCESS_CASES = [
    pytest.param(
        "API_CH_001",
        "정상 classroom_id로 조회",
        id="API_CH_001_classroom_detail_success",
        marks=pytest.mark.tc(**API_CH_001_TC),
    ),
    pytest.param(
        "API_CH_008",
        "학습현황 수치 정확성",
        id="API_CH_008_classroom_learning_status",
        marks=pytest.mark.tc(**API_CH_008_TC),
    ),
]


@pytest.mark.parametrize("tc_id, title", CLASSROOM_DETAIL_SUCCESS_CASES)
def test_get_classroom_detail_success(
    classroom_page,
    classroom_id: str,
    tc_id: str,
    title: str,
) -> None:
    """유효한 classroom_id로 클래스 학습현황 조회 API를 호출하면 정상 응답을 반환한다."""
    logger.info("[%s] %s", tc_id, title)
    response = classroom_page.get_classroom_detail(classroom_id)

    assert_classroom_detail(response, classroom_id)
