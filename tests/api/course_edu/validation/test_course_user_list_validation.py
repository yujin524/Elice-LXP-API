# 수강생 목록 조회 검증 GET /org/{org}/course/user/list API 테스트 — EDU_N_024

import logging
import pytest
from apis.course.course_edu_api import EDU_REST_BASE_URL
from config import settings
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import course_edu_user_list_missing_tutoring_params

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_024_TC = dict(id="EDU_N_024", group="Validation - Query Params", title="수강생 목록 - is_for_tutoring 누락", expected="_result fail")


def _org_path(path: str) -> str:
    return f"/org/{settings.ELICE_ORG_NAME_SHORT}/{path}"


@pytest.mark.tc(**EDU_N_024_TC)
def test_course_user_list_missing_required(api_client, course_id):
    """수강생 목록 필수값 is_for_tutoring 누락 -> 거부."""
    logger.info("▶ [EDU_N_024] is_for_tutoring 없이 수강생 목록 조회 (course_id=%s)", course_id)
    resp = api_client.get(
        EDU_REST_BASE_URL,
        _org_path("course/user/list/"),
        params=course_edu_user_list_missing_tutoring_params(course_id),
    )
    assert_rest_result_failed(resp)


