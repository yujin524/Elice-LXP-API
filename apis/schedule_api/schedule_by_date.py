"""GET /schedule/by_date 요청을 만드는 page 객체."""

from config import settings


class ScheduleByDatePage:
    """GET /schedule/by_date 요청을 만드는 API 객체."""

    def __init__(self, api_client):
        self.api_client = api_client

    def get_schedule_by_date(self, classroom_id=None, date=None):
        params = {}

        if classroom_id is not None:
            params["classroom_id"] = classroom_id

        if date is not None:
            params["date"] = date

        return self.api_client.get(
            settings.API_BASE_URL,
            "/schedule/by_date",
            params=params,
        )
