# 수료 현황 목록 조회 GET /org/{org}/course/completion/list API 테스트 — EDU_005

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_005_TC = dict(id="EDU_005", group="Positive", title="수료 현황 목록 조회", expected="_result ok, completions 포함")


@pytest.mark.tc(**EDU_005_TC)
def test_completion_list(api_client):
    """수료 현황 (org/course/completion/list) - 조직 단위, course_id 불필요."""
    logger.info("▶ [EDU_005] 수료 현황 목록 조회 시작")
    body = assert_rest_result_ok(CourseEduPage(api_client).get_completion_list())
    assert "completions" in body
    logger.info("  └ 수료 항목 %s개", body.get("completion_count"))


