# 학생별 평균 vs 반 전체 평균 정합성 시나리오 테스트 — API_CH_033

from __future__ import annotations
import logging
import pytest
from tests.api.common.assertions import assert_classroom_average, assert_student_list

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

API_CH_033_TC = dict(id="API_CH_033", group="Scenario", title="학생별 평균 vs 전체 평균 정합성", expected="두 값이 근사치로 일치")

AVERAGE_FIELD = "learning_progress"
AVERAGE_TOLERANCE = 0.01
PAGE_SIZE = 40


def _get_all_students(classroom_dashboard_page, classroom_id: str) -> list[dict]:
    """/student는 한 번에 최대 40건까지만 주므로, 끝까지 페이지네이션해서 전체 학생을 모은다."""
    students: list[dict] = []
    offset = 0
    while True:
        page = assert_student_list(
            classroom_dashboard_page.get_student_list(classroom_id=classroom_id, offset=offset, count=PAGE_SIZE)
        )
        students.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return students


@pytest.mark.tc(**API_CH_033_TC)
def test_student_average_matches_classroom_average(classroom_dashboard_page, classroom_id: str) -> None:
    """학생별 현황(learning_progress)의 평균과 반 전체 평균(learning_progress)이 일치해야 한다.
    (Postman 검증 시 46명 전체를 페이지네이션 2회(count=40씩)로 합산한 평균과 반 평균이 0.17로 정확히 일치했음)"""
    logger.info("▶ [API_CH_033][1/2] 학생별 현황 리스트 전체 페이지네이션 조회 (전체 평균 계산용)")
    students = _get_all_students(classroom_dashboard_page, classroom_id)
    if not students:
        pytest.skip("반에 학생이 없어 평균 정합성을 비교할 수 없습니다.")

    logger.info("▶ [API_CH_033][2/2] 반 전체 평균 조회 (정합성 비교 대상)")
    classroom_average = assert_classroom_average(
        classroom_dashboard_page.get_classroom_average(classroom_id), classroom_id
    )

    student_values: list[float] = []
    for s in students:
        try:
            student_values.append(float(s.get(AVERAGE_FIELD)))
        except (TypeError, ValueError):
            continue
    assert student_values, f"학생 응답에 {AVERAGE_FIELD} 필드가 없습니다."
    computed_average = sum(student_values) / len(student_values)
    reported_average = float(classroom_average[AVERAGE_FIELD])

    logger.info(
        "  └ 학생별 %s 평균(계산값)=%.4f, 반 전체 %s(응답값)=%.4f",
        AVERAGE_FIELD, computed_average, AVERAGE_FIELD, reported_average,
    )
    assert abs(computed_average - reported_average) <= AVERAGE_TOLERANCE, (
        f"학생별 평균({computed_average:.4f})과 반 전체 평균({reported_average:.4f})의 "
        f"차이가 허용 오차({AVERAGE_TOLERANCE})를 초과합니다."
    )
