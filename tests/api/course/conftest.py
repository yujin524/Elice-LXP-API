"""학습 과목(course) 화면 전용 체이닝 fixture 모음.

인증/클라이언트, 도메인 공용 식별자(classroom_id, cohort_id, student_user_id)는
루트 conftest.py에 있습니다. 여기에는 "학습 과목" 화면에서만 쓰는 값
(course_id, lecture_id, quiz_material_id)만 둡니다.
"""

from __future__ import annotations
import logging
import pytest
from apis.course.course_api import CoursePage
from utils.api_client import ApiClient, response_debug_message

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def course_id(api_client: ApiClient, classroom_id: str) -> int:
    """테스트에 사용할 course_id를 classroom의 과목 목록에서 찾습니다."""
    response = CoursePage(api_client).get_course_list(classroom_id=classroom_id)
    assert response.status_code == 200, response_debug_message(response, "course list")

    courses = response.json()
    target_title = "소프트웨어 테스트"
    target = next((item for item in courses if target_title in item.get("title", "")), None)
    if target is None:
        target = next(
            (
                item
                for item in courses
                if item.get("classroom_course_progress_data", {}).get("total_material_cnt", 0) > 0
            ),
            None,
        )

    if target is None:
        pytest.skip("콘텐츠가 있는 과목을 찾지 못했습니다.")

    logger.info("[준비] course_id 확보: %s -> %s", target["title"], target["course_id"])
    return target["course_id"]


@pytest.fixture(scope="session")
def lecture_id(api_client: ApiClient, course_id: int) -> int:
    """course_id로 다음 학습 위치의 lecture_id를 찾습니다."""
    response = CoursePage(api_client).get_next_lecture_page(course_id=course_id)
    assert response.status_code == 200, response_debug_message(response, "next lecture page")

    body = response.json()
    if body.get("lecture_id"):
        logger.info("[준비] lecture_id 확보(next_lecture_page): %s", body["lecture_id"])
        return body["lecture_id"]

    logger.info("[준비] next_lecture_page가 null -> lecture 목록으로 fallback")
    fallback_response = CoursePage(api_client).get_lecture_list(course_id=course_id)
    assert fallback_response.status_code == 200, response_debug_message(fallback_response, "lecture list")

    lectures = fallback_response.json()
    if not lectures:
        pytest.skip("이 과목에 강의(lecture)가 없습니다.")

    logger.info("[준비] lecture_id 확보(fallback): %s -> %s", lectures[0]["title"], lectures[0]["id"])
    return lectures[0]["id"]


@pytest.fixture(scope="session")
def quiz_material_id(api_client: ApiClient, course_id: int, lecture_id: int) -> int:
    """lecture_page 안에서 퀴즈 자료(material_type=5)를 자동으로 찾아 그 id를 반환합니다.

    하드코딩하지 않는 이유: material_quiz_id는 과목/강의마다 다른 값이므로,
    lecture_page 응답에서 material_type=5인 항목을 매번 새로 찾아야 합니다.
    """
    response = CoursePage(api_client).get_lecture_page_list(course_id=course_id, lecture_id=lecture_id)
    assert response.status_code == 200, response_debug_message(response, "lecture page list")

    materials = response.json()
    quiz = next((item for item in materials if item.get("material_type") == 5), None)
    if quiz is None:
        pytest.skip("이 강의에 퀴즈(material_type=5) 자료가 없습니다.")

    logger.info("[준비] quiz_material_id 확보: %s -> %s", quiz["title"], quiz["id"])
    return quiz["id"]

