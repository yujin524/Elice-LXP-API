# 커리큘럼 섹션 목록 조회 검증 GET /org/{org}/course/section/list API 테스트 — EDU_N_015, 023

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage, EDU_REST_BASE_URL
from config import settings
from tests.api.common.assertions import assert_rest_result_failed
from tests.api.common.params import course_edu_section_list_missing_paging_params
from tests.api.common.params import NONEXISTENT_ID

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_015_TC = dict(id="EDU_N_015", group="Validation - Path Params", title="없는 course_id 섹션 목록 조회", expected="_result fail")
EDU_N_023_TC = dict(id="EDU_N_023", group="Validation - Query Params", title="섹션 목록 - offset/count 누락", expected="_result fail")


def _org_path(path: str) -> str:
    return f"/org/{settings.ELICE_ORG_NAME_SHORT}/{path}"


@pytest.mark.tc(**EDU_N_015_TC)
def test_section_list_nonexistent(api_client):
    logger.info("▶ [EDU_N_015] 없는 course_id 섹션 목록 조회")
    assert_rest_result_failed(CourseEduPage(api_client).get_section_list(course_id=NONEXISTENT_ID))


@pytest.mark.tc(**EDU_N_023_TC)
def test_section_list_missing_paging(api_client, course_id):
    """list 계열 필수 페이징(offset/count) 누락 -> 거부."""
    logger.info("▶ [EDU_N_023] offset/count 없이 섹션 목록 조회 (course_id=%s)", course_id)
    resp = api_client.get(
        EDU_REST_BASE_URL,
        _org_path("course/section/list/"),
        params=course_edu_section_list_missing_paging_params(course_id),
    )
    assert_rest_result_failed(resp)


