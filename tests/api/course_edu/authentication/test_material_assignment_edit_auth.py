# 과제 자료 편집 POST /org/material_assignment/edit API 테스트 — EDU_N_033

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

EDU_N_033_TC = dict(id="EDU_N_033", group="Authentication", title="과제 자료 편집 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_033_TC)
@AuthNegativeCases.parametrize()
def test_material_assignment_edit_neg_auth(api_client_factory, lecture_id, client_kwargs):
    """과제 자료 편집 - 깨진 인증 client는 편집에 실패해야 한다(데이터 변경 없음)."""
    logger.info("▶ [EDU_N_033-neg] 과제 자료 편집 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).edit_material_assignment(lecture_id=lecture_id,
        title="QA auth-neg",
    )
    assert_rest_result_failed(resp)


