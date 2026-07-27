# 개별 수업 학습현황/전체 강의 진행 현황 조회 GET /student/{student_user_id}/lecture API 테스트 — CO_005, 007

import logging
import pytest
from apis.course.course_api import CoursePage

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_007_TC = dict(id="CO_007", group="Positive", title="전체 강의 진행 현황 조회", expected="200")

CO_005_TC = dict(id="CO_005", group="Positive", title="개별 수업 학습현황 조회", expected="200")


@pytest.mark.tc(**CO_005_TC)
def test_individual_lecture_status(api_client, classroom_id, course_id, lecture_id, student_user_id, cohort_id):
    """'개별 수업 학습현황' 모달 - 특정 강의의 수업자료별 점수 목록."""
    logger.info("▶ [CO_005] 개별 수업 학습현황 조회 시작 (lecture_id=%s)", lecture_id)
    resp = CoursePage(api_client).get_individual_lecture_status(
        student_user_id=student_user_id,
        classroom_id=classroom_id,
        course_id=course_id,
        lecture_id=lecture_id,
        cohort_id=cohort_id,
    )
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert resp.status_code == 200

    body = resp.json()
    lecture_title = body[0]["lecture"]["title"] if body else "알 수 없음"
    logger.info(f"  └ 개별 수업 학습현황 조회됨: {lecture_title} ({len(body)}건)")


@pytest.mark.tc(**CO_007_TC)
def test_lecture_progress_list_for_map(api_client, classroom_id, course_id, student_user_id):
    """
    '학습맵' 탭 - 전체 강의 진행 현황 조회.
    CO_005와 동일 엔드포인트지만 filter_lecture_id, filter_cohort_id 없이 호출하면
    전체 강의의 진행 현황을 한 번에 반환함 (학습맵 노드별 진행률 표시용으로 추정).
    """
    logger.info("▶ [CO_007] 전체 강의 진행 현황 조회 시작 (course_id=%s)", course_id)
    resp = CoursePage(api_client).get_lecture_progress_list(
        student_user_id=student_user_id, classroom_id=classroom_id, course_id=course_id
    )
    logger.info("  └ 응답 수신: status=%s", resp.status_code)
    assert resp.status_code == 200

    body = resp.json()
    assert isinstance(body, list)
    logger.info(f"  └ [CO_007 - 학습맵 진행 상태] 강의 {len(body)}개 진행 현황 조회됨")
    for item in body:
        title = item["lecture"]["title"]
        logger.info(f"        [{title}] 진행률={item.get('learning_progress')}%, "
                    f"실습점수={item.get('practice_score')}, 테스트점수={item.get('test_score')}")



