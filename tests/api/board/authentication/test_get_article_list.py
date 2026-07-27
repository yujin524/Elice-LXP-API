# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_013 ~ 017

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)


API_AR_013_TC = dict(id="API_AR_013", group="Authentication", title="Authorization header 없음", expected="401/403/409, 500 미만")
API_AR_014_TC = dict(id="API_AR_014", group="Authentication", title="Authorization 값 없음", expected="401/403/409, 500 미만")
API_AR_015_TC = dict(id="API_AR_015", group="Authentication", title="Authorization 값 공백", expected="401/403/409, 500 미만")
API_AR_016_TC = dict(id="API_AR_016", group="Authentication", title="Authorization 임의 값", expected="401/403/409, 500 미만")
API_AR_017_TC = dict(id="API_AR_017", group="Authentication", title="잘못된 토큰 인증 실패", expected="409")

AUTH_FAILURE_STATUSES = {401, 403, 409}

AUTH_CASES = [
    pytest.param(
        "API_AR_013",
        {"include_auth": False},
        AUTH_FAILURE_STATUSES,
        "Authorization header 없음",
        id="API_AR_013_authorization_missing",
        marks=pytest.mark.tc(**API_AR_013_TC),
    ),
    pytest.param(
        "API_AR_014",
        {"access_token": ""},
        AUTH_FAILURE_STATUSES,
        "Authorization 값 없음",
        id="API_AR_014_authorization_empty",
        marks=pytest.mark.tc(**API_AR_014_TC),
    ),
    pytest.param(
        "API_AR_015",
        {"access_token": "  "},
        AUTH_FAILURE_STATUSES,
        "Authorization 값 공백",
        id="API_AR_015_authorization_blank",
        marks=pytest.mark.tc(**API_AR_015_TC),
    ),
    pytest.param(
        "API_AR_016",
        {"access_token": "invalid-token"},
        AUTH_FAILURE_STATUSES,
        "Authorization 임의 값",
        id="API_AR_016_authorization_invalid",
        marks=pytest.mark.tc(**API_AR_016_TC),
    ),
    pytest.param(
        "API_AR_017",
        {"access_token": "invalid-token"},
        409,
        "잘못된 토큰 인증 실패",
        id="API_AR_017_invalid_authorization_detail",
        marks=pytest.mark.tc(**API_AR_017_TC),
    ),
]

@pytest.mark.api
@pytest.mark.parametrize("tc_id, client_options, expected_status, title", AUTH_CASES)
def test_get_article_list_authorization_validation(
    api_client_factory,
    classroom_id: str,
    tc_id: str,
    client_options,
    expected_status,
    title: str,
) -> None:
    """
    TC ID: API_AR_013, API_AR_014, API_AR_015, API_AR_016, API_AR_017
    시나리오: Authorization header가 없거나 token이 빈 값, 공백 또는 유효하지 않은
    값이면 게시글 목록 조회(GET) 요청이 인증 실패로 거부되어야 한다.
    """
    client = api_client_factory(**client_options)
    response = get_article_list(client, classroom_id=classroom_id, params=board_article_list_params())

    
    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_response_status(response, expected_status, f"{tc_id} | {title}")
    assert response.status_code < 500
