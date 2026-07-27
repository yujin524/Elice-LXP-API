# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_009 ~ 011, 021, 023 ~ 024

from __future__ import annotations
import logging
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.assertions import (
    assert_board_article_edit_failed,
    assert_board_article_edit_success,
)

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.board_mutation

API_BAE_009_TC = dict(id="API_BAE_009", group="Validation - required fields", title="content 누락", expected="검증 실패, 500 미만")
API_BAE_010_TC = dict(id="API_BAE_010", group="Validation - required fields", title="is_secret 누락", expected="검증 실패, 500 미만")
API_BAE_011_TC = dict(id="API_BAE_011", group="Validation - required fields", title="is_secret 허용값 외 문자열", expected="검증 실패, 500 미만")
API_BAE_021_TC = dict(id="API_BAE_021", group="Validation - required fields", title="content 빈 문자열", expected="명세에 최소 길이 제한이 없어 생성 성공")
API_BAE_023_TC = dict(id="API_BAE_023", group="Validation - required fields", title="is_secret 대문자 문자열", expected="검증 실패, 500 미만")
API_BAE_024_TC = dict(id="API_BAE_024", group="Validation - required fields", title="is_secret 숫자 1", expected="검증 실패, 500 미만")

REQUIRED_FIELD_CASES = [
    pytest.param(
        "API_BAE_009",
        {"content": None},
        False,
        "content 누락",
        id="API_BAE_009_content_missing",
        marks=pytest.mark.tc(**API_BAE_009_TC),
    ),
    pytest.param(
        "API_BAE_010",
        {"is_secret": None},
        False,
        "is_secret 누락",
        id="API_BAE_010_is_secret_missing",
        marks=pytest.mark.tc(**API_BAE_010_TC),
    ),
    pytest.param(
        "API_BAE_011",
        {"is_secret": "invalid"},
        False,
        "is_secret 허용값 외 문자열",
        id="API_BAE_011_is_secret_invalid",
        marks=pytest.mark.tc(**API_BAE_011_TC),
    ),
    pytest.param(
        "API_BAE_021",
        {"content": ""},
        True,
        "content 빈 문자열",
        id="API_BAE_021_content_empty",
        marks=pytest.mark.tc(**API_BAE_021_TC),
    ),
    pytest.param(
        "API_BAE_023",
        {"is_secret": "True"},
        False,
        "is_secret 대문자 문자열",
        id="API_BAE_023_is_secret_uppercase",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="enum에 없는 is_secret='True'를 성공 처리함."),
            pytest.mark.tc(**API_BAE_023_TC),
        ],
    ),
    pytest.param(
        "API_BAE_024",
        {"is_secret": 1},
        False,
        "is_secret 숫자 1",
        id="API_BAE_024_is_secret_numeric",
        marks=pytest.mark.tc(**API_BAE_024_TC),
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, overrides, expected_success, description", REQUIRED_FIELD_CASES)
def test_edit_board_article_required_validation(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
    tc_id: str,
    overrides: dict,
    expected_success: bool,
    description: str,
) -> None:
    """content와 is_secret의 누락, 빈 값 또는 잘못된 값은 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(data=make_board_article_edit_payload(**overrides))

    logger.info("[%s] %s", tc_id, description)
    if expected_success:
        board_article_id = assert_board_article_edit_success(response)
        board_article_cleanup_registry.track(board_article_id, api_client, tc_id=tc_id)
        return
    assert_board_article_edit_failed(response)
