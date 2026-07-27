# 교육자 과목 목록 검증 GET /org/{org}/course/list API 테스트 — EDU_N_040

import logging
import pytest
from apis.course.course_edu_api import EDU_ORG_NAME_SHORT, EDU_REST_BASE_URL
from tests.api.common.assertions import assert_rest_result_failed

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_N_040_TC = dict(id="EDU_N_040", group="Validation - Query Params", title="과목 목록 - offset/count 누락", expected="_result fail")


@pytest.mark.tc(**EDU_N_040_TC)
def test_course_list_missing_paging(api_client):
    """[EDU_N_040] 과목 목록 - offset/count 누락
    내용 : list 계열 필수 페이징 파라미터(offset/count) 없이 '과목 목록 조회(GET)' API를
    호출하면 _result fail로 거부되어야 한다."""
    logger.info("▶ [EDU_N_040] offset/count 없이 교육자 과목 목록 조회")
    resp = api_client.get(EDU_REST_BASE_URL, f"/org/{EDU_ORG_NAME_SHORT}/course/list/", params={})
    assert_rest_result_failed(resp)
