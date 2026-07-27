# 개별 수업 학습현황/전체 강의 진행 현황 조회 GET /student/{student_user_id}/lecture API 테스트 — CO_N_005, 007

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.auth_cases import AuthNegativeCases

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

CO_N_007_TC = dict(id="CO_N_007", group="Authentication", title="전체 강의 진행 현황 - 인증 실패 거부", expected="401/403/409")

CO_N_005_TC = dict(id="CO_N_005", group="Authentication", title="개별 수업 학습현황 - 인증 실패 거부", expected="401/403/409")


@pytest.mark.tc(**CO_N_005_TC)
@AuthNegativeCases.parametrize()
def test_individual_lecture_status_neg_auth(api_client_factory, classroom_id, course_id, lecture_id, student_user_id, cohort_id, client_kwargs):
    """개별 수업 학습현황 - 깨진 인증 client는 조회에 실패해야 한다."""
    logger.info("▶ [CO_N_005-neg] 개별 수업 학습현황 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_individual_lecture_status(
        student_user_id=student_user_id,
        classroom_id=classroom_id,
        course_id=course_id,
        lecture_id=lecture_id,
        cohort_id=cohort_id,
    )
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert resp.status_code in AuthNegativeCases.STATUS_CODES


@pytest.mark.tc(**CO_N_007_TC)
@AuthNegativeCases.parametrize()
def test_lecture_progress_neg_auth(api_client_factory, classroom_id, course_id, student_user_id, client_kwargs):
    """전체 강의 진행 현황 - 깨진 인증 client는 조회에 실패해야 한다."""
    logger.info("▶ [CO_N_007-neg] 전체 강의 진행 현황 인증 실패 케이스 시작: %s", client_kwargs)
    client = api_client_factory(**client_kwargs)
    resp = CoursePage(client).get_lecture_progress_list(
        student_user_id=student_user_id, classroom_id=classroom_id, course_id=course_id
    )
    logger.info("  └ 응답 수신: status=%s (기대: 401/403/409)", resp.status_code)
    assert resp.status_code in AuthNegativeCases.STATUS_CODES


