# 수업 일정 설정 POST /org/lecture/schedule API 테스트 — EDU_N_032

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

EDU_N_032_TC = dict(id="EDU_N_032", group="Authentication", title="수업 일정 설정 - 인증 실패 거부", expected="_result fail")


@pytest.mark.tc(**EDU_N_032_TC)
@AuthNegativeCases.parametrize()
def test_set_lecture_schedule_neg_auth(api_client_factory, lecture_id, client_kwargs):
    """수업 공개/마감 일정 설정 - 깨진 인증 client는 설정에 실패해야 한다(데이터 변경 없음)."""
    logger.info("▶ [EDU_N_032-neg] 수업 일정 설정 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).set_lecture_schedule(lecture_id=lecture_id,
        open_schedule_datetime=1900000000000,
        close_schedule_datetime=1900000060000,
    )
    assert_rest_result_failed(resp)


