"""API 테스트 query parameter 생성 함수."""

from __future__ import annotations
from typing import Any
from datetime import date


def _apply_overrides(params: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """None 값은 제거하고 나머지는 덮어씁니다."""
    for key, value in overrides.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return params


# ==========================================
# Common
# ==========================================


def pagination_params(**overrides: Any) -> dict[str, Any]:
    """목록 조회 API에서 공통으로 사용하는 pagination query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "skip": 0,
        "count": 10,
    }
    return _apply_overrides(params, overrides)


# ==========================================
# Board
# ==========================================


def board_article_list_params(**overrides: Any) -> dict[str, Any]:
    """게시글 목록 조회의 기본 query parameter를 만듭니다."""
    params = pagination_params()
    params.update(
        {
            "filter_title": "%%",
            "sort_by": "created_desc",
        }
    )
    return _apply_overrides(params, overrides)


def default_params(**overrides: Any) -> dict[str, Any]:
    """게시글 목록 조회 query parameter의 이전 이름입니다."""
    return board_article_list_params(**overrides)


def board_article_params(**overrides: Any) -> dict[str, Any]:
    """게시글 상세 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "board_article_id": 1,
    }
    return _apply_overrides(params, overrides)


# ==========================================
# Schedule
# ==========================================


SCHEDULE_DT_START_GE = "2026-07-01T00:00:00Z"
SCHEDULE_DT_START_LE = "2026-07-31T23:59:59Z"
SCHEDULE_INVALID_DT_START_GE = "2026-07-31T23:59:59Z"
SCHEDULE_INVALID_DT_START_LE = "2026-07-01T00:00:00Z"
SCHEDULE_DEFAULT_COUNT = 40
SCHEDULE_MIN_COUNT = 1
SCHEDULE_DEFAULT_OFFSET = 0
SCHEDULE_TIMEZONE = "Asia/Seoul"
INVALID_CLASSROOM_ID = "abc123"
NOT_FOUND_CLASSROOM_ID = "00000000-0000-0000-0000-000000000000"
DEFAULT_LECTUREROOM_ID = 145931


def schedule_list_params(classroom_id: str, **overrides: Any) -> dict[str, Any]:
    """일정 목록 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "dt_start_ge": SCHEDULE_DT_START_GE,
        "dt_start_le": SCHEDULE_DT_START_LE,
        "count": SCHEDULE_DEFAULT_COUNT,
    }
    return _apply_overrides(params, overrides)


def schedule_count_params(classroom_id: str, **overrides: Any) -> dict[str, Any]:
    """일정 개수 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "dt_start_ge": SCHEDULE_DT_START_GE,
        "dt_start_le": SCHEDULE_DT_START_LE,
    }
    return _apply_overrides(params, overrides)


def schedule_ics_params(classroom_id: str, **overrides: Any) -> dict[str, Any]:
    """일정 ICS 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "dt_start_ge": SCHEDULE_DT_START_GE,
        "dt_start_le": SCHEDULE_DT_START_LE,
        "offset": SCHEDULE_DEFAULT_OFFSET,
        "count": SCHEDULE_DEFAULT_COUNT,
        "timezone": SCHEDULE_TIMEZONE,
    }
    return _apply_overrides(params, overrides)


def schedule_by_date_params(classroom_id: str, **overrides: Any) -> dict[str, Any]:
    """일정 미리보기 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "date": date.today().isoformat(),
    }
    return _apply_overrides(params, overrides)


def lectureroom_detail_params(
    lectureroom_id: int | None = DEFAULT_LECTUREROOM_ID,
    **overrides: Any,
) -> dict[str, Any]:
    """강의실 상세 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {}
    if lectureroom_id is not None:
        params["lectureroom_id"] = lectureroom_id
    return _apply_overrides(params, overrides)


# ==========================================
# Course
# ==========================================


COURSE_LIST_COUNT = 20
COURSE_CONTENT_COUNT = 40
COURSE_PROGRESS_COUNT = 10
COURSE_PROGRESS_OFFSET = 0
COURSE_INTRO_LANG = "ko-KR"


def course_list_params(**overrides: Any) -> dict[str, Any]:
    """과목 목록 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "skip": 0,
        "count": COURSE_LIST_COUNT,
    }
    return _apply_overrides(params, overrides)


def course_elice_params(course_id: int, **overrides: Any) -> dict[str, Any]:
    """COURSE_BASE_URL 계열에서 사용하는 elice_course_id query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "elice_course_id": course_id,
    }
    return _apply_overrides(params, overrides)


def course_detail_params(course_id: int, **overrides: Any) -> dict[str, Any]:
    """REST 과목 상세 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "course_id": course_id,
    }
    return _apply_overrides(params, overrides)


def course_intro_params(org: str, **overrides: Any) -> dict[str, Any]:
    """과목 소개 페이지 조회 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "org": org,
        "lang": COURSE_INTRO_LANG,
    }
    return _apply_overrides(params, overrides)


def lecture_list_params(course_id: int, **overrides: Any) -> dict[str, Any]:
    """강의 목록 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "filter_is_opened": "true",
        "filter_depth": 1,
        "skip": 0,
        "count": COURSE_CONTENT_COUNT,
        "elice_course_id": course_id,
    }
    return _apply_overrides(params, overrides)


def lecture_page_params(course_id: int, lecture_id: int, **overrides: Any) -> dict[str, Any]:
    """강의 자료 목록 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "filter_lecture_id": lecture_id,
        "filter_is_opened": "true",
        "skip": 0,
        "count": COURSE_CONTENT_COUNT,
        "elice_course_id": course_id,
    }
    return _apply_overrides(params, overrides)


def learning_status_summary_params(
    classroom_id: str,
    course_id: int,
    cohort_id: int,
    **overrides: Any,
) -> dict[str, Any]:
    """학습현황 요약 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "course_id": course_id,
        "filter_cohort_id": cohort_id,
    }
    return _apply_overrides(params, overrides)


def individual_lecture_status_params(
    classroom_id: str,
    course_id: int,
    lecture_id: int,
    cohort_id: int,
    **overrides: Any,
) -> dict[str, Any]:
    """개별 강의 학습현황 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "course_id": course_id,
        "filter_lecture_id": lecture_id,
        "offset": COURSE_PROGRESS_OFFSET,
        "count": COURSE_PROGRESS_COUNT,
        "filter_cohort_id": cohort_id,
    }
    return _apply_overrides(params, overrides)


def lecture_progress_params(
    classroom_id: str,
    course_id: int,
    **overrides: Any,
) -> dict[str, Any]:
    """전체 강의 진행 현황 조회의 기본 query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "classroom_id": classroom_id,
        "course_id": course_id,
        "offset": COURSE_PROGRESS_OFFSET,
        "count": COURSE_CONTENT_COUNT,
        "elice_course_id": course_id,
    }
    return _apply_overrides(params, overrides)


# ==========================================
# Course Edu
# ==========================================


COURSE_EDU_DEFAULT_OFFSET = 0
COURSE_EDU_DEFAULT_COUNT = 20

# course_edu validation 테스트에서 "존재하지 않는 id"로 쓰는 공통 값. course_id/lecture_id/
# course_section_id/material_quiz_id 등 정수 id 계열 15개 파일이 각자 같은 값을 반복 정의하고
# 있었어서 한 곳으로 모은다.
NONEXISTENT_ID = 99_999_999


def course_edu_section_list_missing_paging_params(
    course_id: int,
    **overrides: Any,
) -> dict[str, Any]:
    """섹션 목록 조회에서 offset/count를 일부러 제외한 validation query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "course_id": course_id,
    }
    return _apply_overrides(params, overrides)


def course_edu_user_list_missing_tutoring_params(
    course_id: int,
    **overrides: Any,
) -> dict[str, Any]:
    """수강생 목록 조회에서 is_for_tutoring을 일부러 제외한 validation query parameter를 만듭니다."""
    params: dict[str, Any] = {
        "course_id": course_id,
        "offset": COURSE_EDU_DEFAULT_OFFSET,
        "count": COURSE_EDU_DEFAULT_COUNT,
    }
    return _apply_overrides(params, overrides)
