# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_012, 029

from __future__ import annotations
import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)

API_AR_012_TC = dict(id="API_AR_012", group="Validation - headers", title="x-elice-org-name-short header 누락", expected="400/401/403/422, 500 미만")
API_AR_029_TC = dict(id="API_AR_029", group="Validation - headers", title="x-elice-org-name-short header 잘못된 값", expected="400/401/403/404/422, 500 미만")

ORG_HEADER_FAILURE_STATUSES = {400, 401, 403, 422}

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_012_TC)
@pytest.mark.bug_candidate
@pytest.mark.xfail(reason="조직 식별 header를 누락해도 게시글 목록이 HTTP 200으로 반환됨.")
def test_get_article_list_header_validation(
    token_settings,
    api_client_factory,
    classroom_id: str,
) -> None:
    """
    TC ID: API_AR_012
    시나리오: 조직 식별 header 없이 게시글 목록 조회(GET) API를 호출하면
    서버 에러가 아닌 제어 가능한 4xx 응답이 반환되어야 한다.
    """
    client = api_client_factory(
        access_token=token_settings.ELICE_ACCESS_TOKEN,
        include_org=False,
    )
    response = get_article_list(client, classroom_id=classroom_id, params=board_article_list_params())

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_response_status(response, ORG_HEADER_FAILURE_STATUSES, "API_AR_012 | missing org header")
    assert response.status_code < 500

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_029_TC)
@pytest.mark.bug_candidate
@pytest.mark.xfail(reason="잘못된 조직 식별 header를 전달해도 게시글 목록이 HTTP 200으로 반환됨.")
def test_get_article_list_with_invalid_org_header(
    token_settings,
    api_client_factory,
    classroom_id: str,
) -> None:
    """잘못된 조직 식별 헤더는 제어 가능한 4xx 응답으로 거부되어야 한다."""
    client = api_client_factory(
        access_token=token_settings.ELICE_ACCESS_TOKEN,
        org_name_short="invalid-org",
    )
    response = get_article_list(client, classroom_id=classroom_id, params=board_article_list_params())

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    assert_response_status(response, ORG_HEADER_FAILURE_STATUSES | {404}, "API_AR_029 | invalid org header")
    assert response.status_code < 500
