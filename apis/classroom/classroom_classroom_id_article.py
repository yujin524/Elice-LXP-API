"""GET /classroom/{classroom_id}/article API 요청 함수."""

from __future__ import annotations
from typing import Any
from config import settings
from utils.api_client import ApiClient


API_NAME = "GET /classroom/{classroom_id}/article"


def _build_article_path(classroom_id: str, *, suffix: str = "/article") -> str:
    """게시글 관련 classroom 경로를 생성합니다."""
    return f"/classroom/{classroom_id}{suffix}"


def get_article_list(
    client: ApiClient,
    *,
    classroom_id: str,
    params: dict[str, Any] | None = None,
    suffix: str = "/article",
):
    """게시글 목록 API를 호출합니다."""
    return client.get(
        settings.API_BASE_URL,
        _build_article_path(classroom_id, suffix=suffix),
        params=params,
    )


def get_missing_classroom_id_route(
    client: ApiClient,
    *,
    params: dict[str, Any] | None = None,
):
    """`/classroom/article`처럼 classroom_id 경로 조각이 빠진 요청을 보냅니다."""
    return client.get(
        settings.API_BASE_URL,
        "/classroom/article",
        params=params,
    )
