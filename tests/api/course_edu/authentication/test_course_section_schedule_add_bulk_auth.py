# 수업 일정 일괄 추가 POST /org/course/section/schedule/add/bulk API 테스트 — EDU_N_031

import logging
import pytest
from tests.api.common.assertions import assert_rest_result_failed
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

EDU_N_031_TC = dict(id="EDU_N_031", group="Authentication", title="수업 일정 추가 - 인증 실패 거부", expected="_result fail")


_DUMMY_SCHEDULES = [{"begin_datetime": 1900000000000, "end_datetime": 1900000060000}]


@pytest.mark.tc(**EDU_N_031_TC)
@AuthNegativeCases.parametrize()
def test_add_section_schedule_neg_auth(api_client_factory, section_id, client_kwargs):
    """수업 일정 추가 - 깨진 인증 client는 추가에 실패해야 한다(데이터 변경 없음)."""
    logger.info("▶ [EDU_N_031-neg] 수업 일정 추가 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CourseEduPage(client).add_section_schedules(course_section_id=section_id,
        section_schedule_list=_DUMMY_SCHEDULES,
    )
    assert_rest_result_failed(resp)


