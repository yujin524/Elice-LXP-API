"""Schedule 도메인 API 요청 객체 모음.

GET /schedule
GET /schedule/count
GET /schedule/ics
GET /org/{org}/course/lectureroom/get/
POST /schedule
"""

from config import settings
from typing import Any


class SchedulePage:
    """GET /schedule 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def get_schedule_list(
        self,
        classroom_id=None,
        dt_start_ge=None,
        dt_start_le=None,
        count=None,
    ):
        params = {}

        if classroom_id is not None:
            params["classroom_id"] = classroom_id

        if dt_start_ge is not None:
            params["dt_start_ge"] = dt_start_ge

        if dt_start_le is not None:
            params["dt_start_le"] = dt_start_le

        if count is not None:
            params["count"] = count

        return self.api_client.get(
            settings.API_BASE_URL,
            "/schedule",
            params=params,
        )


class ScheduleCountPage:
    """GET /schedule/count 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def get_schedule_count(
        self,
        classroom_id=None,
        dt_start_ge=None,
        dt_start_le=None,
    ):
        params = {}

        if classroom_id is not None:
            params["classroom_id"] = classroom_id

        if dt_start_ge is not None:
            params["dt_start_ge"] = dt_start_ge

        if dt_start_le is not None:
            params["dt_start_le"] = dt_start_le

        return self.api_client.get(
            settings.API_BASE_URL,
            "/schedule/count",
            params=params,
        )


class ScheduleIcsPage:
    """GET /schedule/ics 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def get_schedule_ics(
        self,
        classroom_id=None,
        dt_start_ge=None,
        dt_start_le=None,
        count=None,
        offset=None,
        timezone=None,
    ):
        params = {}

        if classroom_id is not None:
            params["classroom_id"] = classroom_id

        if dt_start_ge is not None:
            params["dt_start_ge"] = dt_start_ge

        if dt_start_le is not None:
            params["dt_start_le"] = dt_start_le

        if count is not None:
            params["count"] = count

        if offset is not None:
            params["offset"] = offset

        if timezone is not None:
            params["timezone"] = timezone

        return self.api_client.get(
            settings.API_BASE_URL,
            "/schedule/ics",
            params=params,
        )


class LectureroomPage:
    """GET /org/{org}/course/lectureroom/get/ 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def get_lectureroom(self, org, lectureroom_id=None):
        params = {}

        if lectureroom_id is not None:
            params["lectureroom_id"] = lectureroom_id

        return self.api_client.get(
            settings.REST_BASE_URL,
            f"/org/{org}/course/lectureroom/get/",
            params=params,
        )

class SchedulePostPage:
    """POST /schedule 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def create_schedule(self, **payload: Any):
        """수업 일정 등록 요청."""
        return self.api_client.post(
            settings.API_BASE_URL,
            "/schedule",
            json=payload,
        )