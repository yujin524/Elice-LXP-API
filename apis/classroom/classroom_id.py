"""GET /classroom/{classroom_id} 요청을 만드는 page 객체."""

from config import settings


class ClassroomPage:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_classroom_detail(self, classroom_id=None):
        if classroom_id is None:
            return self.api_client.get(settings.API_BASE_URL, "/classroom/")

        return self.api_client.get(settings.API_BASE_URL, f"/classroom/{classroom_id}")
