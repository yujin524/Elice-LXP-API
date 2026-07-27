# 게시글 생성·수정 POST /board/article/edit API 테스트 — API_BAE_012 ~ 016, 025 ~ 029

from __future__ import annotations
import pytest
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.payload import board_article_edit_data
from tests.api.common.assertions import (
    assert_board_article_edit_failed,
    assert_board_article_edit_success,
)
from tests.api.board.article_cleanup import build_automation_article_title

pytestmark = pytest.mark.board_mutation

API_BAE_027_TC = dict(id="API_BAE_027", group="Validation - context", title="board_id 문자열", expected="검증 실패, 500 미만")
API_BAE_028_TC = dict(id="API_BAE_028", group="Validation - context", title="course_id 문자열", expected="검증 실패, 500 미만")
API_BAE_029_TC = dict(id="API_BAE_029", group="Validation - context", title="cohort_id UUID 형식 오류", expected="검증 실패, 500 미만")
API_BAE_012_TC = dict(id="API_BAE_012", group="Validation - context", title="cohort_id만 전달", expected="no_board_id_or_classroom_id 실패")
API_BAE_013_TC = dict(id="API_BAE_013", group="Validation - context", title="classroom_id UUID 형식 오류", expected="검증 실패, 500 미만")
API_BAE_014_TC = dict(id="API_BAE_014", group="Validation - context", title="board_article_id 문자열", expected="int 변환 검증 실패, 500 미만")
API_BAE_015_TC = dict(id="API_BAE_015", group="Validation - context", title="명세 Required 3개 필드만 전달", expected="명세 기준 생성 성공")
API_BAE_016_TC = dict(id="API_BAE_016", group="Validation - context", title="classroom_id만 전달", expected="cohort_id 누락 검증 실패")
API_BAE_025_TC = dict(id="API_BAE_025", group="Validation - context", title="존재하지 않는 board_article_id로 수정", expected="검증 실패, 500 미만")
API_BAE_026_TC = dict(id="API_BAE_026", group="Positive", title="유효한 board_id로 게시글 생성", expected="생성 성공 및 board_article_id 반환")

CONTEXT_CONVERTER_CASES = [
    pytest.param(
        "API_BAE_027",
        {"board_id": "abc"},
        "board_id 문자열",
        id="API_BAE_027_board_id_string",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="int 변환 불가능한 board_id='abc'를 성공 처리함."),
            pytest.mark.tc(**API_BAE_027_TC),
        ],
    ),
    pytest.param(
        "API_BAE_028",
        {"course_id": "abc"},
        "course_id 문자열",
        id="API_BAE_028_course_id_string",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="int 변환 불가능한 course_id='abc'를 성공 처리함."),
            pytest.mark.tc(**API_BAE_028_TC),
        ],
    ),
    pytest.param(
        "API_BAE_029",
        {"cohort_id": "invalid-cohort-id"},
        "cohort_id UUID 형식 오류",
        id="API_BAE_029_cohort_id_invalid_uuid",
        marks=[
            pytest.mark.bug_candidate,
            pytest.mark.xfail(reason="UUID 변환 불가능한 cohort_id를 성공 처리함."),
            pytest.mark.tc(**API_BAE_029_TC),
        ],
    ),
]

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_012_TC)
def test_edit_board_article_with_only_cohort_id(
    api_client,
) -> None:
    """cohort_id는 board_id 또는 classroom_id를 대체할 수 없어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=board_article_edit_data(cohort_id="00000000-0000-4000-8000-000000000000")
    )

    assert_board_article_edit_failed(
        response,
        expected_fail_code="no_board_id_or_classroom_id",
    )

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_013_TC)
def test_edit_board_article_with_invalid_classroom_id(
    api_client,
    make_board_article_edit_payload,
) -> None:
    """UUID 형식이 아닌 classroom_id는 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(
            classroom_id="invalid-classroom-id",
            board_id=None,
        ),
    )

    assert_board_article_edit_failed(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.bug_candidate
@pytest.mark.xfail(
    reason="board_article_id='abc'를 거부하지 않고 신규 게시글 ID를 생성함.",
)
@pytest.mark.tc(**API_BAE_014_TC)
def test_edit_board_article_with_string_article_id(
    api_client,
    make_board_article_edit_payload,
) -> None:
    """int로 변환할 수 없는 board_article_id는 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(board_article_id="abc"),
    )

    assert_board_article_edit_failed(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.bug_candidate
@pytest.mark.xfail(
    reason="명세의 Required 필드만 보내면 no_board_id_or_classroom_id로 실패함.",
)
@pytest.mark.tc(**API_BAE_015_TC)
def test_edit_board_article_with_documented_required_fields_only(api_client) -> None:
    """명세상 필수인 title/content/is_secret만으로 성공해야 한다는 계약을 추적한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(data=board_article_edit_data())

    assert_board_article_edit_success(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.bug_candidate
@pytest.mark.xfail(
    reason="classroom_id만 보내면 성공 ID를 반환하지만 목록에 노출되지 않는 게시글이 생성됨.",
)
@pytest.mark.tc(**API_BAE_016_TC)
def test_edit_board_article_rejects_classroom_without_cohort(
    api_client,
    make_board_article_edit_payload,
) -> None:
    """정상 노출에 cohort_id가 필요하다면 누락 요청은 성공하면 안 된다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(board_id=None, cohort_id=None)
    )

    assert_board_article_edit_failed(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_025_TC)
def test_edit_nonexistent_board_article_id(
    api_client,
    make_board_article_edit_payload,
) -> None:
    """존재하지 않는 ID를 수정 요청에 사용하면 신규 생성되지 않고 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(board_article_id=999999999),
    )

    assert_board_article_edit_failed(response)

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_BAE_026_TC)
def test_create_board_article_with_board_id(
    api_client,
    board_id: int,
    board_article_cleanup_registry,
) -> None:
    """명세가 허용하는 board_id 컨텍스트만으로 게시글을 생성할 수 있어야 한다."""
    data = board_article_edit_data(
        title=build_automation_article_title("API_BAE_026"),
        board_id=board_id,
    )
    response = OrgBoardArticleApi(api_client).post_edit_article(data=data)

    board_article_id = assert_board_article_edit_success(response)
    board_article_cleanup_registry.track(board_article_id, api_client, tc_id="API_BAE_026")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.parametrize("tc_id, overrides, title", CONTEXT_CONVERTER_CASES)
def test_edit_board_article_context_converter_validation(
    api_client,
    make_board_article_edit_payload,
    tc_id: str,
    overrides: dict,
    title: str,
) -> None:
    """board_id/course_id/cohort_id의 변환 불가능한 값은 거부되어야 한다."""
    response = OrgBoardArticleApi(api_client).post_edit_article(
        data=make_board_article_edit_payload(**overrides),
    )

    assert_board_article_edit_failed(response)
