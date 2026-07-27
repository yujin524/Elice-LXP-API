# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_011, 027 ~ 028

from __future__ import annotations
import logging
from uuid import uuid4
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_article_list

logger = logging.getLogger(__name__)

API_AR_011_TC = dict(id="API_AR_011", group="Validation - filter_title", title="filter_title 빈 문자열", expected="200, JSON 배열")
API_AR_027_TC = dict(id="API_AR_027", group="Validation - filter_title", title="실제 게시글 제목 검색", expected="200, 검색한 제목을 포함한 게시글 반환")
API_AR_028_TC = dict(id="API_AR_028", group="Validation - filter_title", title="존재하지 않는 게시글 제목 검색", expected="200, 빈 JSON 배열")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_011_TC)
def test_get_article_list_filter_title_validation(api_client, classroom_id: str) -> None:
    """
    TC ID: API_AR_011
    시나리오: filter_title 값을 빈 문자열로 전달해 게시글 목록 조회(GET) API를 호출하면
    200 상태 코드와 정상적인 게시글 목록(JSON 배열)이 반환되어야 한다.
    """
    response = get_article_list(api_client, classroom_id=classroom_id, params=board_article_list_params(filter_title=""))

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_article_list(response, classroom_id, max_count=10)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_027_TC)
def test_get_article_list_filter_title_matches_existing_article(api_client, classroom_id: str) -> None:
    """목록에 존재하는 제목으로 검색하면 해당 게시글이 결과에 포함되어야 한다."""
    source_response = get_article_list(api_client, classroom_id=classroom_id, params=board_article_list_params(count=10))
    source_articles = assert_article_list(source_response, classroom_id, max_count=10)
    article = next((item for item in source_articles if item.get("title")), None)
    if article is None:
        pytest.skip("제목 검색에 사용할 게시글이 없습니다.")

    title = article["title"]
    response = get_article_list(
        api_client,
        classroom_id=classroom_id,
        params=board_article_list_params(filter_title=f"%{title}%", count=10),
    )
    articles = assert_article_list(response, classroom_id, max_count=10)

    assert any(item.get("id") == article.get("id") for item in articles)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_028_TC)
def test_get_article_list_filter_title_returns_empty_for_unknown_title(api_client, classroom_id: str) -> None:
    """존재할 가능성이 없는 고유 제목 검색은 빈 배열을 반환해야 한다."""
    unknown_title = f"__api_no_match_{uuid4().hex}__"
    response = get_article_list(
        api_client,
        classroom_id=classroom_id,
        params=board_article_list_params(filter_title=f"%{unknown_title}%", count=10),
    )
    articles = assert_article_list(response, classroom_id, max_count=10)

    assert articles == []
