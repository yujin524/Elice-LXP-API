"""API 요청 공통 모듈.
Postman의 Collection 레벨 Authorization + 공통 헤더 설정을
Python 코드로 옮긴 역할입니다.
"""

from __future__ import annotations
from typing import Any
import requests

class ApiClient:
    """Postman Collection처럼 공통 header와 timeout을 붙여 요청합니다."""

    def __init__(
        self,
        session: requests.Session,
        settings: Any,
        *,
        access_token: str | None = None,
        org_name_short: str | None = None,
        include_auth: bool = True,
        include_org: bool = True,
    ) -> None:
        self.session = session
        self.settings = settings
        self.default_headers = {"Accept": "*/*"}

        if include_auth:
            token = access_token if access_token is not None else getattr(settings, "ELICE_ACCESS_TOKEN", "")
            self.default_headers["Authorization"] = f"Bearer {token}"

        if include_org:
            org = org_name_short if org_name_short is not None else getattr(settings, "ELICE_ORG_NAME_SHORT", "")
            self.default_headers["x-elice-org-name-short"] = org

    def build_url(self, base_url: str, path: str) -> str:
        """base_url 끝과 path 앞의 /만 정리하고, path 중간의 //는 보존합니다."""
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    def request(self, method: str, base_url: str, path: str, **kwargs):
        """공통 API 요청."""
        extra_headers = kwargs.pop("headers", None) or {}
        headers = {**self.default_headers, **extra_headers}

        return self.session.request(
            method,
            self.build_url(base_url, path),
            headers=headers,
            timeout=self.settings.API_TIMEOUT_SECONDS,
            **kwargs,
        )

    def get(self, base_url: str, path: str, **kwargs):
        """GET 요청."""
        return self.request("GET", base_url, path, **kwargs)

    def post(self, base_url: str, path: str, **kwargs):
        """POST 요청. 주로 리소스 생성이나 제출에 사용합니다."""
        return self.request("POST", base_url, path, **kwargs)

    def put(self, base_url: str, path: str, **kwargs):
        """PUT 요청. 리소스 전체를 교체할 때 사용합니다."""
        return self.request("PUT", base_url, path, **kwargs)

    def patch(self, base_url: str, path: str, **kwargs):
        """PATCH 요청. 리소스 일부를 수정할 때 사용합니다."""
        return self.request("PATCH", base_url, path, **kwargs)

    def delete(self, base_url: str, path: str, **kwargs):
        """DELETE 요청. 리소스 삭제에 사용합니다."""
        return self.request("DELETE", base_url, path, **kwargs)

def response_debug_message(response: Any, context: str = "") -> str:
    """assert 실패 시 status, url, body 일부를 보여줍니다."""
    body = response.text[:300].replace("\n", " ") if hasattr(response, "text") else ""
    prefix = f"{context}: " if context else ""
    return f"{prefix}status={response.status_code}, url={getattr(response, 'url', '')}, body_preview={body}"