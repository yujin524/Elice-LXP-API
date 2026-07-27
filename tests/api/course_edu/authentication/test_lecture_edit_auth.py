# 수업 편집 POST /org/lecture/edit API 테스트 — EDU_N_011

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

EDU_N_011_TC = dict(id="EDU_N_011", group="Authentication", title="수업 편집 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_011_TC)
@AuthNegativeCases.parametrize()
def test_lecture_edit_neg_auth(api_client_factory, editable_lecture, client_kwargs):
    """수업 편집 - 깨진 인증 client는 편집에 실패해야 한다(데이터 변경 없음)."""
    course_id, lecture = editable_lecture
    lecture_id = lecture.get("id") or lecture.get("lecture_id")
    logger.info("▶ [EDU_N_011-neg] 수업 편집 인증 실패 케이스 시작: %s (lecture_id=%s)", client_kwargs, lecture_id)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).edit_lecture(course_id=course_id,
        lecture_id=lecture_id,
        lecture_type=lecture.get("lecture_type", 0),
        title=lecture.get("title") or "x",  # 현재 값 유지 (혹시 통과해도 no-op)
        description=lecture.get("description") or "",
        is_opened=bool(lecture.get("is_opened")),
        is_preview=bool(lecture.get("is_preview")),
    )
    assert_rest_result_failed(resp)


