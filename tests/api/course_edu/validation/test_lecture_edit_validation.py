# 수업 편집 검증 POST /org/{org}/lecture/edit API 테스트 — EDU_N_017 ~ 018, 022

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_017_TC = dict(id="EDU_N_017", group="Validation - Query Params", title="수업 편집 - 잘못된 lecture_type", expected="_result fail")
EDU_N_018_TC = dict(id="EDU_N_018", group="Validation - Query Params", title="수업 편집 - 제목 길이 초과(128자+)", expected="_result fail")
EDU_N_022_TC = dict(id="EDU_N_022", group="Validation - Query Params", title="수업 편집 - 없는 lecture_id", expected="_result fail")


@pytest.mark.tc(**EDU_N_017_TC)
def test_lecture_edit_invalid_type(api_client, editable_lecture):
    """lecture_type enum(0/1/2) 벗어난 값 -> 거부 (실패하므로 실제 수정 안 됨)."""
    course_id, lecture = editable_lecture
    lecture_id = lecture.get("id") or lecture.get("lecture_id")
    logger.info("▶ [EDU_N_017] 잘못된 lecture_type=99 로 수업 편집 시도 (lecture_id=%s)", lecture_id)
    resp = CourseEduPage(api_client).edit_lecture(course_id=course_id,
        lecture_id=lecture_id,
        lecture_type=99,  # enum 벗어남
        title=lecture.get("title") or "x",
        description=lecture.get("description") or "",
        is_opened=bool(lecture.get("is_opened")),
        is_preview=bool(lecture.get("is_preview")),
    )
    assert_rest_result_failed(resp)


@pytest.mark.tc(**EDU_N_018_TC)
def test_lecture_edit_title_too_long(api_client, editable_lecture):
    """title 최대 128자 초과 -> 거부 (실패하므로 실제 수정 안 됨)."""
    course_id, lecture = editable_lecture
    lecture_id = lecture.get("id") or lecture.get("lecture_id")
    logger.info("▶ [EDU_N_018] 제목 200자로 수업 편집 시도 (lecture_id=%s)", lecture_id)
    resp = CourseEduPage(api_client).edit_lecture(course_id=course_id,
        lecture_id=lecture_id,
        lecture_type=lecture.get("lecture_type", 0),
        title="가" * 200,  # 128자 초과
        description=lecture.get("description") or "",
        is_opened=bool(lecture.get("is_opened")),
        is_preview=bool(lecture.get("is_preview")),
    )
    assert_rest_result_failed(resp)


@pytest.mark.tc(**EDU_N_022_TC)
def test_lecture_edit_nonexistent_id(api_client, course_id):
    """없는 lecture_id로 편집 시도 -> 대상 없음으로 거부 (실제 수정 대상이 없어 안전)."""
    logger.info("▶ [EDU_N_022] 없는 lecture_id=%s 로 수업 편집 시도", NONEXISTENT_ID)
    resp = CourseEduPage(api_client).edit_lecture(course_id=course_id,
        lecture_id=NONEXISTENT_ID,
        lecture_type=0,
        title="검증용_없는수업_편집시도",
        description="",
    )
    assert_rest_result_failed(resp)


