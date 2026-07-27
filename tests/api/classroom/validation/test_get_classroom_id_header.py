# 클래스 학습현황 조회 GET /classroom/{classroom_id} API 테스트 — API_CH_005 ~ 007

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_id import ClassroomPage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.api, pytest.mark.requires_token]

API_CH_005_TC = dict(id="API_CH_005", group="Validation - headers", title="x-elice-org-name-short header 누락", expected="헤더 없이도 정상 조회 / HTTP 200")
API_CH_006_TC = dict(id="API_CH_006", group="Validation - headers", title="존재하지 않는 org-name-short 값", expected="HTTP 409")
API_CH_007_TC = dict(id="API_CH_007", group="Validation - headers", title="x-elice-org-name-short header 빈 문자열", expected="HTTP 409")

CLASSROOM_HEADER_CASES = [
    pytest.param(
        "API_CH_005",
        {"include_org": False},
        200,
        "org header 누락",
        id="API_CH_005_org_header_missing",
        marks=pytest.mark.tc(**API_CH_005_TC),
    ),
    pytest.param(
        "API_CH_006",
        {"org_name_short": "invalidorg"},
        409,
        "존재하지 않는 org 값",
        id="API_CH_006_org_header_invalid",
        marks=pytest.mark.tc(**API_CH_006_TC),
    ),
    pytest.param(
        "API_CH_007",
        {"org_name_short": ""},
        409,
        "org header 빈 문자열",
        id="API_CH_007_org_header_empty",
        marks=pytest.mark.tc(**API_CH_007_TC),
    ),
]


@pytest.mark.parametrize("tc_id, client_options, expected_status, title", CLASSROOM_HEADER_CASES)
def test_get_classroom_detail_header_validation(
    api_client_factory,
    access_token: str,
    classroom_id: str,
    tc_id: str,
    client_options: dict,
    expected_status: int | set[int],
    title: str,
) -> None:
    """classroom 학습현황 조회 API의 조직 header 검증 케이스를 확인한다."""
    client = api_client_factory(access_token=access_token, **client_options)
    response = ClassroomPage(client).get_classroom_detail(classroom_id)

    logger.info("[%s] %s 응답 status=%s", tc_id, title, response.status_code)
    assert_response_status(response, expected_status, f"{tc_id} | {title}")
