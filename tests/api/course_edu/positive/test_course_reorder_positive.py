# 과목 순서 변경 후 복원 POST /classroom/{classroom_id}/course/reorder API 테스트 — EDU_013

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_013_TC = dict(id="EDU_013", group="Positive", title="과목 순서 변경 후 복원", expected="순서 반영 확인 후 원복")


def _course_order(api_client, classroom_id: str) -> list[int]:
    """클래스룸 과목의 현재 순서(course_id 리스트)를 읽는다. reorder는 전체 집합과
    정확히 일치해야 하므로 페이징 끝까지 모은 목록을 써야 한다."""
    courses = CourseEduPage(api_client).list_all_classroom_courses(classroom_id=classroom_id)
    return [c["course_id"] for c in courses]


@pytest.mark.tc(**EDU_013_TC)
def test_course_reorder_and_restore(api_client, classroom_id):
    """클래스룸 과목 순서를 앞 두 개만 바꿔 반영을 확인하고, 원래 순서로 되돌린다.

    (classroom-api 계열이라 HTTP 상태 코드로 판정. 순서만 바꿨다 복원하므로 데이터 변경 없음.)
    """
    original = _course_order(api_client, classroom_id)
    if len(original) < 2:
        pytest.skip("과목이 2개 미만이라 순서 변경 검증 불가")

    swapped = original[:]
    swapped[0], swapped[1] = swapped[1], swapped[0]

    logger.info("▶ [EDU_013] 과목 순서 변경-복원 시작 (앞2: %s -> %s)", original[:2], swapped[:2])
    try:
        resp = CourseEduPage(api_client).reorder_courses(classroom_id=classroom_id, course_ids=swapped)
        assert resp.status_code == 200, f"순서 변경 실패: status={resp.status_code}"
        assert _course_order(api_client, classroom_id)[:2] == swapped[:2]
        logger.info("  └ 순서 변경 반영 확인")
    finally:
        resp = CourseEduPage(api_client).reorder_courses(classroom_id=classroom_id, course_ids=original)
        assert resp.status_code == 200, f"순서 복원 실패: status={resp.status_code}"
        assert _course_order(api_client, classroom_id) == original
        logger.info("  └ 원래 순서로 복원 완료")


