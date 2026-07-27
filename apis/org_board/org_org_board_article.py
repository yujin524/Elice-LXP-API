"""org board article API 요청 클래스."""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any
from config import settings
from utils.api_client import ApiClient


Attachment = tuple[str, bytes, str]


def _form_value(value: Any) -> str:
    """multipart/form-data의 일반 필드 값을 문자열로 변환합니다."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


class OrgBoardArticleApi:
    """GET/POST /org/{org}/board/article API 요청을 담당합니다."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def _org_name(self, org: str | None = None) -> str:
        return org or settings.ELICE_ORG_NAME_SHORT

    def _build_multipart_data(
        self,
        data: dict[str, Any],
        attachments: Sequence[Attachment] | None = None,
    ) -> list[tuple[str, tuple[Any, ...]]]:
        """multipart/form-data payload를 생성합니다."""
        multipart: list[tuple[str, tuple[Any, ...]]] = [
            (key, (None, _form_value(value)))
            for key, value in data.items()
            if value is not None
        ]

        for filename, content, content_type in attachments or ():
            multipart.append(("attachment_files", (filename, content, content_type)))

        return multipart

    def _post_multipart(self, path: str, *, data: dict[str, Any], attachments: Sequence[Attachment] | None = None):
        """multipart/form-data로 POST 요청을 전송합니다."""
        return self.client.post(
            settings.REST_BASE_URL,
            path,
            files=self._build_multipart_data(data, attachments),
        )

    def get_article(
        self,
        *,
        params: dict[str, Any] | None = None,
        org: str | None = None,
    ):
        """게시글 상세 조회 API를 호출합니다."""
        return self.client.get(
            settings.REST_BASE_URL,
            f"/org/{self._org_name(org)}/board/article/get/",
            params=params,
        )

    def post_edit_article(
        self,
        *,
        data: dict[str, Any],
        attachments: Sequence[Attachment] | None = None,
        org: str | None = None,
    ):
        """게시글 생성 또는 수정 API를 multipart/form-data로 호출합니다."""
        return self._post_multipart(
            f"/org/{self._org_name(org)}/board/article/edit/",
            data=data,
            attachments=attachments,
        )

    def post_delete_article(
        self,
        *,
        data: dict[str, Any],
        org: str | None = None,
    ):
        """게시글 삭제 API를 multipart/form-data로 호출합니다."""
        return self._post_multipart(
            f"/org/{self._org_name(org)}/board/article/delete/",
            data=data,
        )
