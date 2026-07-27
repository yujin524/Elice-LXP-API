# 수강 후기 목록 조회 GET /org/{org}/course/info/review/list API 테스트 — EDU_008

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_008_TC = dict(id="EDU_008", group="Positive", title="수강 후기 목록 조회", expected="_result ok, info_reviews 포함")


@pytest.mark.tc(**EDU_008_TC)
def test_info_review_list(api_client, course_info_id):
    """수강 후기 (org/course/info/review/list)."""
    logger.info("▶ [EDU_008] 수강 후기 조회 시작 (course_info_id=%s)", course_info_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_info_review_list(course_info_id=course_info_id))
    assert "info_reviews" in body
    logger.info("  └ 후기 %s개", body.get("info_review_count"))


