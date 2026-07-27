# 학습맵(과목 상세) 조회 GET /org/{org_name}/course/get/ API 테스트 — CO_006

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_006_TC = dict(id="CO_006", group="Positive", title="학습맵(과목 상세) 조회", expected="200")


@pytest.mark.tc(**CO_006_TC)
def test_course_detail_for_map(api_client, course_id):
    """
    '학습맵' 탭 - 과목 상세(커리큘럼 구조) 조회.
    이 응답 안의 'lectures' 배열이 학습맵 노드 구조, 'preference.landing...sections' 안에
    '과목소개' 탭 본문 콘텐츠까지 같이 들어있음이 확인됨.
    """
    logger.info("▶ [CO_006] 학습맵(과목 상세) 조회 시작 (course_id=%s)", course_id)
    resp = CoursePage(api_client).get_course_detail(course_id=course_id)
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_006 학습맵(과목 상세) 조회")

    body = resp.json()
    assert "course" in body
    assert "lectures" in body["course"]

    course_title = body["course"]["title"]
    lectures = sorted(body["course"]["lectures"], key=lambda lec: lec.get("order_no", 0))

    logger.info(f"  └ [CO_006 - 학습맵 구조] 과목 상세 조회됨: 강의 {len(lectures)}개 포함")
    logger.info(f"  └ [{course_title}]")
    for lec in lectures:
        logger.info(f"        └ {lec['title']}")



