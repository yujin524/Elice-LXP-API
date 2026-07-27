"""교육자용 클래스 홈 대시보드(반 평균/학생 리스트) 요청을 만드는 page 객체."""

from config import settings


class ClassroomDashboardPage:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_classroom_average(self, classroom_id=None):
        """반 전체 평균 조회 (CH_022, CH_024, CH_025)."""
        if classroom_id is None:
            return self.api_client.get(settings.DASHBOARD_BASE_URL, "/classroom/")

        return self.api_client.get(settings.DASHBOARD_BASE_URL, f"/classroom/{classroom_id}")

    def get_student_list(self, *, classroom_id: str, offset: int = 0, count: int = 10):
        """학생별 현황 리스트 조회 (CH_023, CH_026, CH_032, CH_033)."""
        return self.api_client.get(
            settings.DASHBOARD_BASE_URL,
            "/student",
            params={"classroom_id": classroom_id, "offset": offset, "count": count},
        )
