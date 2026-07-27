# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_030 ~ 033

from __future__ import annotations
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.assertions import assert_board_article_edit_failed, assert_board_article_edit_success

FILE_SIZE_LIMIT = 30 * 1024 * 1024
pytestmark = pytest.mark.board_mutation



API_BAE_030_TC = dict(id="API_BAE_030", group="Validation - attachment_files", title="30MB 이하 첨부파일", expected="첨부파일과 함께 게시글 생성 성공")
API_BAE_031_TC = dict(id="API_BAE_031", group="Validation - attachment_files", title="30MB 초과 첨부파일", expected="파일 크기 검증 실패, 500 미만")
API_BAE_032_TC = dict(id="API_BAE_032", group="Validation - attachment_files", title="여러 첨부파일", expected="여러 attachment_files와 함께 게시글 생성 성공")
API_BAE_033_TC = dict(id="API_BAE_033", group="Validation - attachment_files", title="0바이트 첨부파일", expected="0바이트 파일 처리 성공, 500 미만")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_030_TC)
def test_create_board_article_with_attachment(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """파일 크기 제한 이하의 일반 첨부파일은 허용되어야 한다."""
    attachments = [("small.txt", b"attachment test", "text/plain")]
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(),
        attachments=attachments,
    )

    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(board_article_id, api_client, tc_id="API_BAE_030")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_031_TC)
def test_reject_board_article_attachment_over_size_limit(api_client, make_board_article_edit_payload) -> None:
    """30MB 제한을 1바이트 초과한 첨부파일은 거부되어야 한다."""
    attachments = [("too-large.bin", b"0" * (FILE_SIZE_LIMIT + 1), "application/octet-stream")]
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(),
        attachments=attachments,
    )

    assert_board_article_edit_failed(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_032_TC)
def test_create_board_article_with_multiple_attachments(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """make_iter 명세에 따라 여러 attachment_files를 전송할 수 있어야 한다."""
    attachments = [
        ("first.txt", b"first attachment", "text/plain"),
        ("second.txt", b"second attachment", "text/plain"),
    ]
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(),
        attachments=attachments,
    )

    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(board_article_id, api_client, tc_id="API_BAE_032")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_033_TC)
def test_create_board_article_with_empty_attachment(
    api_client,
    make_board_article_edit_payload,
    board_article_cleanup_registry,
) -> None:
    """0바이트 파일도 서버 오류 없이 정상 처리되어야 한다."""
    attachments = [("empty.txt", b"", "text/plain")]
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(),
        attachments=attachments,
    )

    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(board_article_id, api_client, tc_id="API_BAE_033")
