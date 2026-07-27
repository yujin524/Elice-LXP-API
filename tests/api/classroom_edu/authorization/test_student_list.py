# 학생별 현황 리스트 조회 GET /student (dashboard) 권한 경계 테스트 — API_CH_032

from __future__ import annotations
import logging
import pytest
from apis.classroom_edu.dashboard import ClassroomDashboardPage

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

API_CH_032_TC = dict(id="API_CH_032", group="Authority Boundary", title="학생 계정의 /student 리스트는 본인 데이터만 조회됨", expected="HTTP 200, 본인 1건만 반환(타 학생 데이터 비노출)")


class TestStudentListAuthorityBoundary:
    @pytest.mark.tc(**API_CH_032_TC)
    def test_classroom_edu_learner_can_only_see_own_data(
        self,
        learner_api_client,
        learner_account_id: int,
        ch032_classroom_id: str,
    ) -> None:
        """[API_CH_032] 학생 계정으로 학생별 현황 리스트(GET /student)를 호출하면 HTTP 200과 함께
        본인 데이터 1건만 반환된다(self-scoped). 스펙 문서가 없어 실측으로 확인함 — 타 학생 데이터가
        섞여 나오면 권한 경계 위반 버그다. classroom_id는 다른 자동화와 공유되지 않는 CH_032 전용
        classroom(ch032_classroom_id)을 써야 멤버 상태가 실행마다 흔들리지 않는다."""
        logger.info("▶ [API_CH_032] 학생 계정의 /student self-scope 검증 (classroom_id=%s)", ch032_classroom_id)
        response = ClassroomDashboardPage(learner_api_client).get_student_list(
            classroom_id=ch032_classroom_id, offset=0, count=10
        )
        logger.info("  └ 응답 수신: status=%s (기대: 200)", response.status_code)
        assert response.status_code == 200

        students = response.json()
        assert len(students) == 1, f"본인 데이터 1건만 기대했으나 {len(students)}건 반환됨: {students}"
        assert students[0]["account"]["id"] == learner_account_id
