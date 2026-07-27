"""학습 과목(Course, 학생) 관련 API 요청 클래스.

테스트 코드에서 URL/파라미터 조립을 분리해, 요청 만들기를 여기 한곳으로 모읍니다.
(apis/classroom/classroom_id.py 등 다른 도메인의 Page 객체와 같은 역할 — course 도메인용)

각 메서드는 요청을 보내고 response를 그대로 돌려줍니다.
검증(assert)은 테스트가 담당하고, 여기서는 "어디로 어떤 파라미터로 보내는가"만 책임집니다.
"""

from __future__ import annotations
from config import settings
from utils.api_client import ApiClient


class CoursePage:
    """학생(수강생)용 과목/강의 학습 API 요청을 담당합니다."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    # =========================================================
    # api-classroom (API_BASE_URL)
    # =========================================================

    def get_course_list(self, *, classroom_id: str, skip: int = 0, count: int = 20):
        """학습 과목 목록 조회 (CO_001)."""
        return self.client.get(
            settings.API_BASE_URL,
            f"/classroom/{classroom_id}/course",
            params={"skip": skip, "count": count},
        )

    # =========================================================
    # api-course (COURSE_BASE_URL)
    # =========================================================

    def get_next_lecture_page(self, *, course_id: int):
        """다음 학습 위치 조회 (CO_002)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            f"/course/{course_id}/next_lecture_page",
            params={"elice_course_id": course_id},
        )

    def get_lecture_page_list(self, *, course_id: int, lecture_id: int):
        """학습 페이지(강의 자료) 목록 조회 (CO_003)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            "/lecture_page",
            params={
                "filter_lecture_id": lecture_id,
                "filter_is_opened": "true",
                "skip": 0,
                "count": 40,
                "elice_course_id": course_id,
            },
        )

    def get_lecture_list(self, *, course_id: int):
        """강의(lecture) 목록 조회 (CO_014 전수 검증에서 사용)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            "/lecture",
            params={
                "filter_is_opened": "true",
                "filter_depth": 1,
                "skip": 0,
                "count": 40,
                "elice_course_id": course_id,
            },
        )

    def get_next_material(self, *, material_id: int, course_id: int):
        """다음 강의자료 존재 여부 확인 (CO_011)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            f"/lecture_page/{material_id}/next",
            params={"elice_course_id": course_id},
        )

    def get_prev_material(self, *, material_id: int, course_id: int):
        """이전 강의자료 존재 여부 확인 (CO_012)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            f"/lecture_page/{material_id}/prev",
            params={"elice_course_id": course_id},
        )

    def get_curriculum(self, *, course_id: int):
        """과목 커리큘럼 재조회 = 학습 종료 처리 (CO_013)."""
        return self.client.get(
            settings.COURSE_BASE_URL,
            f"/course/{course_id}/curriculum",
            params={"elice_course_id": course_id},
        )

    # =========================================================
    # api-dashboard (DASHBOARD_BASE_URL)
    # =========================================================

    def get_learning_status_summary(
        self,
        *,
        student_user_id: int,
        classroom_id: str,
        course_id: int,
        cohort_id: int,
    ):
        """학습현황 요약 조회 (CO_004)."""
        return self.client.get(
            settings.DASHBOARD_BASE_URL,
            f"/student/{student_user_id}",
            params={"classroom_id": classroom_id, "course_id": course_id, "filter_cohort_id": cohort_id},
        )

    def get_individual_lecture_status(
        self,
        *,
        student_user_id: int,
        classroom_id: str,
        course_id: int,
        lecture_id: int,
        cohort_id: int,
    ):
        """개별 수업 학습현황 조회 (CO_005) - 특정 강의 필터."""
        return self.client.get(
            settings.DASHBOARD_BASE_URL,
            f"/student/{student_user_id}/lecture",
            params={
                "classroom_id": classroom_id,
                "course_id": course_id,
                "filter_lecture_id": lecture_id,
                "offset": 0,
                "count": 10,
                "filter_cohort_id": cohort_id,
            },
        )

    def get_lecture_progress_list(
        self,
        *,
        student_user_id: int,
        classroom_id: str,
        course_id: int,
    ):
        """전체 강의 진행 현황 조회 (CO_007) - 필터 없이 전체."""
        return self.client.get(
            settings.DASHBOARD_BASE_URL,
            f"/student/{student_user_id}/lecture",
            params={
                "classroom_id": classroom_id,
                "course_id": course_id,
                "offset": 0,
                "count": 40,
                "elice_course_id": course_id,
            },
        )

    # =========================================================
    # api-rest (REST_BASE_URL) - /org/{org}/...
    # =========================================================

    def get_course_detail(self, *, course_id: int):
        """학습맵(과목 상세) 조회 (CO_006)."""
        return self.client.get(
            settings.REST_BASE_URL,
            f"/org/{settings.ELICE_ORG_NAME_SHORT}/course/get/",
            params={"course_id": course_id},
        )

    def quiz_enter(self, *, material_quiz_id: int):
        """퀴즈 문제 진입 (CO_009)."""
        return self.client.post(
            settings.REST_BASE_URL,
            f"/org/{settings.ELICE_ORG_NAME_SHORT}/material_quiz/options_set/select/",
            json={"material_quiz_id": material_quiz_id},
        )

    def quiz_submit(self, *, material_quiz_id: int, answer: list[int] | None = None):
        """퀴즈 답안 제출 (CO_010)."""
        return self.client.post(
            settings.REST_BASE_URL,
            f"/org/{settings.ELICE_ORG_NAME_SHORT}/material_quiz/response/add/",
            json={"material_quiz_id": material_quiz_id, "answer": answer if answer is not None else [3]},
        )
