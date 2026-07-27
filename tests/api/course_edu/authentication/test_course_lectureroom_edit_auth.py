# 라이브 강의실 생성 POST /org/course/lectureroom/edit API 테스트 — EDU_N_030

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

EDU_N_030_TC = dict(id="EDU_N_030", group="Authentication", title="라이브 강의실 생성 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_030_TC)
@AuthNegativeCases.parametrize()
def test_lectureroom_edit_neg_auth(api_client_factory, course_id, section_id, client_kwargs):
    """라이브 강의실 생성 - 깨진 인증 client는 생성에 실패해야 한다(데이터 변경 없음)."""
    logger.info("▶ [EDU_N_030-neg] 라이브 강의실 생성 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).create_lectureroom(course_id=course_id,
        course_section_id=section_id,
        title="QA auth-neg",
    )
    assert_rest_result_failed(resp)


