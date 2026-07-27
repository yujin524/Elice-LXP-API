"""API 테스트 request body/form-data 생성 함수."""

from __future__ import annotations
from typing import Any


def _apply_overrides(data: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """None 값은 제거하고 나머지는 덮어씁니다."""
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return data


# ==========================================
# Board
# ==========================================


def board_article_edit_data(**overrides: Any) -> dict[str, Any]:
    """게시글 생성·수정 API의 기본 form-data를 만듭니다."""
    data: dict[str, Any] = {
        "title": "API 자동화 테스트 게시글",
        "content": "<p>API 자동화 테스트 내용</p>",
        "is_secret": "false",
    }
    return _apply_overrides(data, overrides)


def board_article_delete_data(**overrides: Any) -> dict[str, Any]:
    """게시글 삭제 API의 기본 form-data를 만듭니다."""
    data: dict[str, Any] = {
        "board_article_id": 999999999,
    }
    return _apply_overrides(data, overrides)


# ==========================================
# Course
# ==========================================


def material_quiz_enter_payload(material_quiz_id: int, **overrides: Any) -> dict[str, Any]:
    """퀴즈 진입 API의 기본 JSON payload를 만듭니다."""
    data: dict[str, Any] = {
        "material_quiz_id": material_quiz_id,
    }
    return _apply_overrides(data, overrides)


def material_quiz_submit_payload(
    material_quiz_id: int,
    answer: list[int] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """퀴즈 답안 제출 API의 기본 JSON payload를 만듭니다."""
    data: dict[str, Any] = {
        "material_quiz_id": material_quiz_id,
        "answer": answer or [3],
    }
    return _apply_overrides(data, overrides)


# ==========================================
# Schedule
# ==========================================


def schedule_create_payload(default_classroom_id: str, **overrides: Any) -> dict[str, Any]:
    """수업 일정 등록 API의 기본 JSON payload를 만듭니다."""
    data: dict[str, Any] = {
        "classroom_id": default_classroom_id,
        "summary": "API 테스트 수업 일정",
        "dt_start": "2026-07-21T22:00:00.000Z",
        "dt_end": "2026-07-21T23:00:00.000Z",
    }
    return _apply_overrides(data, overrides)