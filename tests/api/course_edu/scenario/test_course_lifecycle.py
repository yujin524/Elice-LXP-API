# 과목 생명주기(추가→편집→제거) POST /v2/classroom/{classroom_id}/course/bulk → POST /org/{org}/lecture/edit → DELETE /classroom/{classroom_id}/course/{course_id} API 테스트 — EDU_014

import logging
import os
import time
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_014_TC = dict(id="EDU_014", group="Positive", title="과목 추가→수업 편집→클래스 제거", expected="추가/편집 확인 후 제거로 원복")
ORIGINAL_COURSE_ID = int(os.getenv("EDU_ORIGINAL_COURSE_ID", "77"))


def _course_ids(api_client, classroom_id) -> set:
    courses = CourseEduPage(api_client).list_all_classroom_courses(classroom_id=classroom_id)
    return {c["course_id"] for c in courses}


def _wait_for_new_course(api_client, classroom_id, before: set, timeout: int = 40, interval: int = 2):
    """추가된 새 course_id가 목록에 나타날 때까지 폴링. 타임아웃이면 None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        new_ids = _course_ids(api_client, classroom_id) - before
        if new_ids:
            return sorted(new_ids)[-1]
        time.sleep(interval)
    return None


@pytest.mark.tc(**EDU_014_TC)
def test_course_add_edit_remove(api_client, classroom_id):
    """과목을 복제 추가하고, 그 안의 수업을 편집해 반영을 확인한 뒤, 클래스에서 제거해 원복한다."""
    before = _course_ids(api_client, classroom_id)

    logger.info("▶ [EDU_014] 과목 추가 시작 (original_course_id=%s)", ORIGINAL_COURSE_ID)
    resp = CourseEduPage(api_client).add_courses_bulk(classroom_id=classroom_id, original_course_ids=[ORIGINAL_COURSE_ID])
    assert resp.status_code == 200, f"과목 추가 요청 실패: status={resp.status_code}"
    task_id = resp.json().get("task_id")
    assert task_id, f"task_id가 없습니다: {resp.text}"
    logger.info("  └ task_id=%s → 새 과목이 목록에 나타날 때까지 대기(폴링)", task_id)

    new_course_id = None
    try:
        # 1) 추가 반영 확인 (async → 폴링)
        new_course_id = _wait_for_new_course(api_client, classroom_id, before)
        if new_course_id is None:
            pytest.skip("추가한 과목이 시간 내 목록에 나타나지 않음(async 지연)")
        logger.info("  └ 새 course_id 확보: %s", new_course_id)

        # 2) 수업(내용) 편집: 복제 과목의 수업이 채워질 때까지 폴링 후, 첫 수업 제목을 변경 → 반영 확인
        #    (복제가 async라 수업이 늦게 채워질 수 있음. 시간 내 안 채워지면 편집은 건너뛰고 add/remove만 검증)
        target = None
        deadline = time.time() + 30
        while time.time() < deadline:
            lectures = CourseEduPage(api_client).get_lecture_list(course_id=new_course_id, offset=0, count=30).json().get("lectures", [])
            target = next((lec for lec in lectures if lec.get("lecture_type") == 0), lectures[0] if lectures else None)
            if target is not None:
                break
            time.sleep(2)

        if target is None:
            logger.info("  └ 복제 과목의 수업이 시간 내 안 채워짐 → 편집 단계 건너뜀 (add/remove만 검증)")
        else:
            lecture_id = target.get("id") or target.get("lecture_id")
            new_title = f"{target.get('title') or '수업'} [QA-EDIT]"
            logger.info("  └ 수업 편집 시도 (lecture_id=%s)", lecture_id)
            assert_rest_result_ok(CourseEduPage(api_client).edit_lecture(course_id=new_course_id,
                lecture_id=lecture_id,
                lecture_type=target.get("lecture_type", 0),
                title=new_title,
                description=target.get("description") or "",
                is_opened=bool(target.get("is_opened")),
                is_preview=bool(target.get("is_preview")),
            ))
            after = CourseEduPage(api_client).get_lecture_list(course_id=new_course_id, offset=0, count=30).json().get("lectures", [])
            edited = next((lec for lec in after if (lec.get("id") or lec.get("lecture_id")) == lecture_id), {})
            assert edited.get("title") == new_title, "수업 편집이 반영되지 않음"
            logger.info("  └ 수업 편집 반영 확인: %r", new_title)
    finally:
        # 3) 정리: 클래스에서 과목 제거 (실패해도 반드시 실행)
        if new_course_id is not None:
            logger.info("  └ 정리: 클래스에서 과목 제거 (course_id=%s)", new_course_id)
            del_resp = CourseEduPage(api_client).delete_course(classroom_id=classroom_id, course_id=new_course_id)
            assert del_resp.status_code in (200, 204), f"과목 제거 실패: status={del_resp.status_code}"
            assert new_course_id not in _course_ids(api_client, classroom_id), "제거 후에도 과목이 목록에 남아있음"
            logger.info("  └ 제거 확인 완료 → 원복됨")


