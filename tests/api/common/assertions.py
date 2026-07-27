"""API 테스트 공통 검증 함수."""

from __future__ import annotations
import json
import logging
from typing import Any
from utils.api_client import response_debug_message


logger = logging.getLogger(__name__)
DEFAULT_MAX_RESPONSE_SECONDS = 3


# ==========================================
# Common
# ==========================================


def assert_response_status(
    response: Any,
    expected_status: int | set[int],
    context: str = "",
) -> None:
    """응답 상태 코드를 검증하고 실패 시 요청·응답 요약을 제공합니다."""
    if isinstance(expected_status, set):
        assert response.status_code in expected_status, response_debug_message(response, context)
        return

    assert response.status_code == expected_status, response_debug_message(response, context)


def assert_response_time(response: Any, max_seconds: float, context: str = "") -> None:
    """응답 왕복 시간이 기준(max_seconds) 미만인지 검증합니다."""
    elapsed = response.elapsed.total_seconds()
    logger.info("  └ 응답 시간: %.3fs (기준 %.1fs) %s", elapsed, max_seconds, context)
    assert elapsed < max_seconds, f"응답이 너무 느림: {elapsed:.3f}s >= {max_seconds}s {context}".strip()


def format_error_detail(detail: dict[str, Any]) -> str:
    """FastAPI 422 오류 detail 항목에서 로그에 필요한 핵심 필드만 뽑아 한 줄로 만듭니다.
    `input` 필드는 요청 payload를 그대로 echo해 로그가 지저분해지므로 제외합니다."""
    return f"type={detail.get('type')} loc={detail.get('loc')} msg={detail.get('msg')}"


def assert_rest_result_failed(
    response: Any,
    expected_fail_code: str | None = None,
) -> dict[str, Any]:
    """api-rest(REST_BASE_URL) 계열 전용 인증/권한 실패를 검증합니다."""
    assert response.status_code == 200, f"REST 계열은 200을 기대: status={response.status_code}"
    body = response.json()
    result = body.get("_result", {})
    logger.info("  └ _result=%s", result)
    assert result.get("status") == "fail", f"인증이 깨졌는데 성공 응답이 옴: _result={result}"
    if expected_fail_code is not None:
        assert body.get("fail_code") == expected_fail_code, response_debug_message(
            response,
            f"expected fail_code={expected_fail_code}",
        )
    return body


def assert_rest_result_ok(response: Any) -> dict[str, Any]:
    """api-rest(REST_BASE_URL) 계열 성공 응답을 검증합니다."""
    assert response.status_code == 200, f"REST 계열은 200을 기대: status={response.status_code}"
    body = response.json()
    result = body.get("_result", {})
    logger.info("  └ _result=%s", result)
    assert result.get("status_code") == 200, f"REST 성공을 기대했으나 실패: _result={result}"
    return body


def _assert_under_response_time(response: Any, max_seconds: float = DEFAULT_MAX_RESPONSE_SECONDS) -> None:
    """응답 시간이 기준 미만인지 검증합니다."""
    assert response.elapsed.total_seconds() < max_seconds


def _assert_rest_or_http_failure(
    response: Any,
    context: str,
    expected_fail_code: str | None = None,
    *,
    validate_result_status_code: bool = False,
) -> dict[str, Any]:
    """REST body 실패 또는 HTTP 실패 응답을 공통으로 검증합니다."""
    assert response.status_code < 500, response_debug_message(response, context)
    if response.status_code == 200:
        body = response.json()
        assert isinstance(body, dict)
        result = body.get("_result", {})
        assert result.get("status") == "fail", response_debug_message(
            response,
            "expected REST failure",
        )
        if validate_result_status_code:
            assert result.get("status_code", 0) < 500, response_debug_message(
                response,
                "unexpected REST failure status",
            )
    else:
        assert 400 <= response.status_code < 500, response_debug_message(
            response,
            "unexpected HTTP failure status",
        )
        try:
            body = response.json()
        except ValueError:
            body = {}
        assert isinstance(body, dict)

    if expected_fail_code is not None:
        assert body.get("fail_code") == expected_fail_code, response_debug_message(
            response,
            f"expected fail_code={expected_fail_code}",
        )
    return body


# ==========================================
# Article List
# ==========================================


ARTICLE_FIELDS = {"id", "classroom_id", "title", "content"}


def assert_article_list(
    response: Any,
    classroom_id: str,
    max_count: int,
) -> list[dict[str, Any]]:
    """정상 게시글 목록 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "article list status")
    body = response.json()
    assert isinstance(body, list)
    assert len(body) <= max_count

    for article in body:
        assert ARTICLE_FIELDS.issubset(article.keys())
        assert article["classroom_id"] == classroom_id

    _assert_under_response_time(response)
    return body


# ==========================================
# Classroom
# ==========================================


def assert_classroom_detail(response: Any, classroom_id: str) -> dict[str, Any]:
    """정상 classroom 상세 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "classroom detail status")
    body = response.json()
    assert isinstance(body, dict)
    if body.get("id") is not None:
        assert body["id"] == classroom_id

    _assert_under_response_time(response)
    return body


# ==========================================
# Schedule
# ==========================================


SCHEDULE_FIELDS = {"id", "uid", "summary", "dt_start", "dt_end"}


def assert_schedule_list(response: Any, max_count: int | None = None) -> list[dict[str, Any]]:
    """정상 schedule 목록 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "schedule list status")
    body = response.json()
    assert isinstance(body, list)
    if max_count is not None:
        assert len(body) <= max_count

    if body:
        assert SCHEDULE_FIELDS.issubset(body[0].keys())

    _assert_under_response_time(response)
    return body


def assert_schedule_count(response: Any) -> int:
    """정상 schedule count 응답에서 count 값을 반환합니다."""
    assert_response_status(response, 200, "schedule count status")
    body = response.json()
    count_value = body.get("count") if isinstance(body, dict) else body
    assert isinstance(count_value, int)

    _assert_under_response_time(response)
    return count_value


def assert_schedule_ics(response: Any) -> str:
    """정상 schedule ICS 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "schedule ics status")
    body = response.text
    assert "BEGIN:VCALENDAR" in body
    assert "END:VCALENDAR" in body

    _assert_under_response_time(response)
    return body


# ==========================================
# Classroom Edu (교육자 클래스 홈 대시보드)
# ==========================================


def assert_classroom_average(response: Any, classroom_id: str) -> dict[str, Any]:
    """정상 반 평균 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "classroom average status")
    body = response.json()
    assert isinstance(body, dict)
    if body.get("id") is not None:
        assert body["id"] == classroom_id

    _assert_under_response_time(response)
    return body


def assert_student_list(response: Any, max_count: int | None = None) -> list[dict[str, Any]]:
    """정상 학생별 현황 리스트 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "student list status")
    body = response.json()
    assert isinstance(body, list)
    if max_count is not None:
        assert len(body) <= max_count

    _assert_under_response_time(response)
    return body


def assert_schedule_mutation_success(response: Any, context: str = "schedule mutation") -> None:
    """일정 생성/수정/삭제 성공 응답(200/201)을 검증합니다."""
    assert response.status_code in (200, 201), response_debug_message(response, context)
    _assert_under_response_time(response)


# ==========================================
# Classroom Edu (구성원 관리)
# ==========================================


def assert_member_mutation_success(response: Any, context: str = "member mutation") -> None:
    """구성원 제거/등록 성공 응답(200/201)을 검증합니다."""
    assert response.status_code in (200, 201), response_debug_message(response, context)
    _assert_under_response_time(response)


def assert_member_list(response: Any) -> list[dict[str, Any]]:
    """정상 구성원 목록 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "member list status")
    body = response.json()
    members = body if isinstance(body, list) else body.get("results") or body.get("items") or []
    assert isinstance(members, list)

    _assert_under_response_time(response)
    return members


# ==========================================
# Course
# ==========================================


def assert_course_list(response: Any) -> list[dict[str, Any]]:
    """정상 과목 목록 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "course list status")
    body = response.json()
    assert isinstance(body, list)
    if body:
        first = body[0]
        assert "course_id" in first
        assert "title" in first

    _assert_under_response_time(response)
    return body


def assert_json_object_response(response: Any, context: str = "json object") -> dict[str, Any]:
    """HTTP 200 JSON object 응답인지 검증합니다."""
    assert_response_status(response, 200, context)
    body = response.json()
    assert isinstance(body, dict)
    _assert_under_response_time(response)
    return body


def assert_json_list_response(response: Any, context: str = "json list") -> list[Any]:
    """HTTP 200 JSON list 응답인지 검증합니다."""
    assert_response_status(response, 200, context)
    body = response.json()
    assert isinstance(body, list)
    _assert_under_response_time(response)
    return body


# ==========================================
# Board Article
# ==========================================


BOARD_ARTICLE_FIELDS = {"id", "title", "content"}


def extract_board_article(body: dict[str, Any]) -> dict[str, Any]:
    """Board 응답에서 게시글 객체를 추출합니다."""
    if isinstance(body.get("article"), dict):
        return body["article"]
    if isinstance(body.get("board_article"), dict):
        return body["board_article"]
    return body


def assert_board_article_values_not_exposed(response: Any, *sensitive_values: str) -> None:
    """실패 응답에 게시글의 민감한 값이 노출되지 않았는지 검증합니다."""
    response_text = response.text
    try:
        response_text += json.dumps(response.json(), ensure_ascii=False)
    except ValueError:
        pass
    for value in sensitive_values:
        if value:
            assert value not in response_text, response_debug_message(
                response,
                "sensitive board article value exposed",
            )


def assert_board_article(response: Any, board_article_id: int) -> dict[str, Any]:
    """정상 게시글 상세 응답인지 공통으로 검증합니다."""
    assert_response_status(response, 200, "board article status")
    body = response.json()
    assert isinstance(body, dict)

    article = extract_board_article(body)
    assert BOARD_ARTICLE_FIELDS.issubset(article.keys())
    if article.get("id") is not None:
        assert article["id"] == board_article_id

    _assert_under_response_time(response)
    return body


def assert_board_article_get_failed(response: Any) -> dict[str, Any]:
    """게시글 상세 REST API의 HTTP 또는 body 기반 실패 응답을 검증합니다."""
    return _assert_rest_or_http_failure(
        response,
        "board article get failure",
        validate_result_status_code=True,
    )


def assert_board_article_edit_success(response: Any) -> int:
    """게시글 생성·수정 성공 응답에서 board_article_id를 반환합니다."""
    assert_response_status(response, 200, "board article edit status")
    body = response.json()
    assert isinstance(body, dict)
    result = body.get("_result", {})
    assert result.get("status") == "ok", response_debug_message(response, "board article edit result")

    board_article_id = body.get("board_article_id")
    assert isinstance(board_article_id, int), response_debug_message(
        response,
        "board_article_id type",
    )
    return board_article_id


def assert_board_article_edit_failed(
    response: Any,
    expected_fail_code: str | None = None,
) -> dict[str, Any]:
    """게시글 생성·수정 실패가 HTTP 또는 REST body에 명시됐는지 검증합니다."""
    return _assert_rest_or_http_failure(
        response,
        "board article edit failure",
        expected_fail_code,
    )


def assert_board_article_delete_failed(
    response: Any,
    expected_fail_code: str | None = None,
) -> dict[str, Any]:
    """게시글 삭제 실패가 HTTP 또는 REST body에 명시됐는지 검증합니다."""
    return _assert_rest_or_http_failure(
        response,
        "board article delete failure",
        expected_fail_code,
    )


def assert_board_article_delete_success(response: Any) -> dict[str, Any]:
    """게시글 삭제 성공 응답의 HTTP/REST 상태를 검증합니다."""
    assert_response_status(response, 200, "board article delete status")
    body = response.json()
    assert isinstance(body, dict)

    result = body.get("_result", {})
    assert result.get("status") == "ok", response_debug_message(
        response,
        "board article delete result",
    )
    assert result.get("status_code") == 200, response_debug_message(
        response,
        "board article delete result status code",
    )
    return body
