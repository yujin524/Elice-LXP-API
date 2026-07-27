# 학습현황 요약 조회 GET /student/{student_user_id} API 테스트 — CO_004

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_004_TC = dict(id="CO_004", group="Positive", title="학습현황 요약 조회", expected="200")


@pytest.mark.tc(**CO_004_TC)
def test_learning_status_summary(api_client, classroom_id, course_id, student_user_id, cohort_id):
    """'학습현황' 탭 - 진행률/평균 점수 요약 조회."""
    logger.info("▶ [CO_004] 학습현황 요약 조회 시작 (student_user_id=%s)", student_user_id)
    resp = CoursePage(api_client).get_learning_status_summary(
        student_user_id=student_user_id, classroom_id=classroom_id, course_id=course_id, cohort_id=cohort_id
    )
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_004 학습현황 요약 조회")

    body = resp.json()
    assert "learning_progress" in body

    fullname = body.get("account", {}).get("fullname", "알 수 없음")
    logger.info(f"  └ [{fullname}] 학습 진행률={body.get('learning_progress')}%, "
                f"평균 실습 자료 점수={body.get('practice_score')}, "
                f"평균 테스트 점수={body.get('test_score')}")



