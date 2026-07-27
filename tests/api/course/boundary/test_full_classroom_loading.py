# 전체 과목 x 전체 강의 전수 로딩 GET /classroom/{classroom_id}/course API 테스트 — CO_014

import logging
import pytest
from apis.course.course_api import CoursePage
from tests.api.common.assertions import assert_response_status

logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.api, pytest.mark.requires_token]

CO_014_TC = dict(id="CO_014", group="Positive", title="전체 과목 x 전체 강의 전수 로딩", expected="전부 200")


@pytest.mark.tc(**CO_014_TC)
def test_full_classroom_content_loading(api_client, classroom_id):
    """
    클래스룸 전체 과목 x 전체 강의 로딩 전수 확인.

    QR체크인/아웃처럼 콘텐츠 없는 과목은 건너뛰고,
    실제 강의가 있는 과목들의 lecture_page가 전부 200으로 로딩되는지 확인한다.

    강의 수가 많으면 시간이 꽤 걸릴 수 있다 (Postman에서 순차 처리로 바꿨던 것과 동일한 이유).
    """
    logger.info("▶ [CO_014] 전체 과목 x 전체 강의 로딩 전수 검증 시작")
    resp = CoursePage(api_client).get_course_list(classroom_id=classroom_id)
    logger.info("  └ 과목 목록 응답: status=%s", resp.status_code)
    assert_response_status(resp, 200, "CO_014 과목 목록")
    courses = resp.json()
    logger.info("  └ 총 %d개 과목 순회 시작", len(courses))

    failed = []
    total_lectures = 0

    for idx, course in enumerate(courses, start=1):
        course_id = course["course_id"]
        title = course["title"]
        logger.info(f"  [{idx}/{len(courses)}] [{title}] 강의 목록 확인 중...")

        lec_resp = CoursePage(api_client).get_lecture_list(course_id=course_id)
        if lec_resp.status_code != 200:
            logger.info("        └ 강의 목록 조회 실패: status=%s", lec_resp.status_code)
            failed.append(f"{title} (강의 목록 조회 실패: {lec_resp.status_code})")
            continue

        lectures = lec_resp.json()
        if not lectures:
            logger.info("        └ 콘텐츠 없는 과목, 건너뜀")
            continue

        logger.info("        └ 강의 %d개 -> lecture_page 로딩 확인 중", len(lectures))
        for lec in lectures:
            total_lectures += 1
            page_resp = CoursePage(api_client).get_lecture_page_list(course_id=course_id, lecture_id=lec["id"])
            if page_resp.status_code != 200:
                logger.info("            └ 실패: %s -> %s", lec["title"], page_resp.status_code)
                failed.append(
                    f"{title} > {lec['title']} (lecture_id: {lec['id']}) -> {page_resp.status_code}"
                )

    logger.info(f"  └ 총 {len(courses)}개 과목, {total_lectures}개 강의 확인 완료. 실패 {len(failed)}건.")
    assert not failed, f"로딩 실패한 강의 목록: {failed}"



