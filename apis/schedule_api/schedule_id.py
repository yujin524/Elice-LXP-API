"""POST /schedule, PATCH·DELETE /schedule/{schedule_id} 요청을 만드는 page 객체 (일정 생성/수정/삭제)."""

from typing import Any
from config import settings


class ScheduleIdPage:
    def __init__(self, api_client):
        self.api_client = api_client

    def create_schedule(self, *, classroom_id: str, summary: str, dt_start: str, dt_end: str):
        """일정 생성 (CH_027 사전 준비)."""
        return self.api_client.post(
            settings.API_BASE_URL,
            "/schedule",
            json={
                "classroom_id": classroom_id,
                "summary": summary,
                "dt_start": dt_start,
                "dt_end": dt_end,
            },
        )

    def update_schedule(self, *, schedule_id: str, classroom_id: str | None = None, **overrides: Any):
        """일정 수정 (CH_027, CH_028, CH_030). classroom_id는 body 필수값이라 body에도 넣는다."""
        body: dict[str, Any] = {}
        if classroom_id is not None:
            body["classroom_id"] = classroom_id
        body.update(overrides)

        return self.api_client.patch(
            settings.API_BASE_URL,
            f"/schedule/{schedule_id}",
            json=body,
            params={"classroom_id": classroom_id} if classroom_id is not None else None,
        )

    def delete_schedule(self, *, schedule_id: str, classroom_id: str | None = None):
        """일정 삭제 (CH_029, CH_031)."""
        return self.api_client.delete(
            settings.API_BASE_URL,
            f"/schedule/{schedule_id}",
            json={"classroom_id": classroom_id} if classroom_id is not None else {},
        )
