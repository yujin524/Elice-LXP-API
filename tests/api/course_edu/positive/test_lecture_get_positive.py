# 강의(수업) 상세 조회 GET /org/{org}/lecture/get API 테스트 — EDU_009

import logging
import pytest
from apis.course.course_edu_api import CourseEduPage
from tests.api.common.assertions import assert_rest_result_ok

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

EDU_009_TC = dict(id="EDU_009", group="Positive", title="강의(수업) 상세 조회", expected="_result ok, lecture 포함")


@pytest.mark.tc(**EDU_009_TC)
def test_lecture_detail(api_client, lecture_id, section_id):
    """강의 상세 (org/lecture/get). lecture_id + course_section_id 필수."""
    logger.info("▶ [EDU_009] 강의 상세 조회 시작 (lecture_id=%s, section_id=%s)", lecture_id, section_id)
    body = assert_rest_result_ok(CourseEduPage(api_client).get_lecture_detail(lecture_id=lecture_id, course_section_id=section_id))
    assert "lecture" in body
    logger.info("  └ 강의 제목: %s", body["lecture"].get("title"))


