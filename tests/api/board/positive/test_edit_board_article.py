# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_001 ~ 005

from __future__ import annotations
import json
import logging
import time
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.params import board_article_list_params, board_article_params
from tests.api.common.assertions import (
    assert_article_list,
    assert_board_article,
    assert_board_article_edit_success,
)

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.board_mutation


API_BAE_004_TC = dict(id="API_BAE_004", group="Positive", title="title 최소 길이 1자", expected="생성 성공")
API_BAE_005_TC = dict(id="API_BAE_005", group="Positive", title="title 최대 길이 128자", expected="생성 성공")
API_BAE_001_TC = dict(id="API_BAE_001", group="Positive", title="classroom_id와 board_id로 게시글 생성", expected="_result.status=ok, board_article_id 반환, 게시글 목록 노출")
API_BAE_002_TC = dict(id="API_BAE_002", group="Positive", title="board_article_id로 기존 게시글 수정", expected="동일 board_article_id 유지, GET 상세에 수정 내용 반영")
API_BAE_003_TC = dict(id="API_BAE_003", group="Positive", title="비밀 게시글 생성", expected="is_secret=true 요청 성공 및 board_article_id 반환")

TITLE_BOUNDARY_CASES = [
    pytest.param(
        "API_BAE_004",
        "가",
        id="API_BAE_004_title_min_length",
        marks=pytest.mark.tc(**API_BAE_004_TC),
    ),
    pytest.param(
        "API_BAE_005",
        "가" * 128,
        id="API_BAE_005_title_max_length",
        marks=pytest.mark.tc(**API_BAE_005_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_001_TC)
def test_create_board_article_and_show_in_list(
    api_client,
    classroom_id: str,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """정상 컨텍스트로 생성한 게시글이 동일 classroom 목록에 노출되어야 한다."""
    payload = make_board_article_edit_payload()
    response = OrgBoardArticleApi(api_client).post_edit_article(data=payload)

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)
    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(
        board_article_id,
        api_client,
        tc_id="API_BAE_001",
        owner_role="default",
    )

    for attempt in range(5):
        list_response = get_article_list(
            api_client,
            classroom_id=classroom_id,
            params=board_article_list_params(
                filter_title=f"%{payload['title']}%",
                count=10,
            ),
        )
        articles = assert_article_list(list_response, classroom_id, max_count=10)
        if any(article.get("id") == board_article_id for article in articles):
            break
        if attempt < 4:
            time.sleep(0.5)
    else:
        pytest.fail(f"생성된 게시글이 목록에 없음: board_article_id={board_article_id}")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_002_TC)
def test_update_existing_board_article(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """생성한 게시글 ID로 수정하면 같은 ID의 제목과 내용이 변경되어야 한다."""
    create_response = OrgBoardArticleApi(api_client).post_edit_article(data=make_board_article_edit_payload())
    board_article_id = assert_board_article_edit_success(create_response)
    board_article_cleanup_registry.track(
        board_article_id,
        api_client,
        tc_id="API_BAE_002",
        owner_role="default",
    )

    updated_title = f"수정된 게시글 {board_article_id}"
    updated_content = "<p>수정된 API 자동화 테스트 내용</p>"
    update_payload = make_board_article_edit_payload(
        board_article_id=board_article_id,
        title=updated_title,
        content=updated_content,
    )
    update_response = OrgBoardArticleApi(api_client).post_edit_article(data=update_payload)
    assert assert_board_article_edit_success(update_response) == board_article_id

    detail_response = OrgBoardArticleApi(api_client).get_article(
        params=board_article_params(board_article_id=board_article_id),
    )
    detail_body = assert_board_article(detail_response, board_article_id)
    serialized_body = json.dumps(detail_body, ensure_ascii=False)
    assert updated_title in serialized_body
    assert updated_content in serialized_body

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_003_TC)
def test_create_secret_board_article(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """is_secret=true도 명세의 허용값이므로 정상 생성되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(data=make_board_article_edit_payload(is_secret="true"))

    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(
        board_article_id,
        api_client,
        tc_id="API_BAE_003",
        owner_role="default",
    )

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, title", TITLE_BOUNDARY_CASES)
def test_create_board_article_title_boundaries(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
    tc_id: str,
    title: str,
) -> None:
    """명세의 title 허용 경계값인 1자와 128자는 생성되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(data=make_board_article_edit_payload(title=title))

    logger.info("[%s] title length=%s", tc_id, len(title))
    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(
        board_article_id,
        api_client,
        tc_id=tc_id,
        owner_role="default",
    )
