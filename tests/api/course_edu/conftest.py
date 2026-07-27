"""교육자(강사) 과목 편집/수업 관리 테스트 전용 fixture.

course_edu는 항상 dev 서버·academy org를 대상으로 하는 교육자 전용 스위트다.
공용(.env)의 ELICE_ID/PW·ELICE_ORG_NAME_SHORT가 학생(course) 도메인용으로 무엇을
가리키든 상관없이, 여기서는 access_token/api_client/api_client_factory를
**이 파일에서 자체적으로 override**해서 항상 dev 교육자 계정(EDU_ELICE_ID)으로
로그인하고 academy org로 요청한다. 그래서 `pytest -v`(공용 .env) 한 번으로
course와 course_edu가 둘 다 skip 없이 실행된다.

- 이 override 덕분에 루트 conftest.py의 student_user_id/classroom_id(둘 다 내부적으로
  access_token/api_client를 참조)도 자동으로 이 교육자 계정을 쓰게 된다.
- 여기서는 그 외에 "콘텐츠(강의)가 있는 과목"의 course_id를
  REST(org/course/list, org/lecture/list)로 발견하는 fixture들을 둔다.
"""

from __future__ import annotations
import base64
import json
import logging
import os
import pytest
from apis.course.course_edu_api import CourseEduPage, EDU_API_BASE_URL, EDU_ORG_NAME_SHORT, edu_login
from config import settings
from utils.api_client import ApiClient

logger = logging.getLogger(__name__)

# course_edu 전용 dev 교육자 계정. 공용 .env의 ELICE_ID/PW와 무관하게 항상 이 계정으로 로그인한다.
# EDU_ELICE_ID / EDU_ELICE_PW 환경변수가 있으면 그 값으로 덮어쓴다.
EDU_ELICE_ID = os.getenv("EDU_ELICE_ID", "qa5_final_team3_tc05@example.com")
EDU_ELICE_PW = os.getenv("EDU_ELICE_PW", "qa5-cheerup!!")

# 권한 경계 테스트용 학생(learner) 계정. dev의 활성화된 학생 계정을 기본값으로 쓰고,
# LEARNER_ID / LEARNER_PW 환경변수가 있으면 그 값으로 덮어쓴다.
LEARNER_ID = os.getenv("LEARNER_ID", "qa5_final_team3_le03@example.com")
LEARNER_PW = os.getenv("LEARNER_PW", "qa5-cheerup!!")

# SANDBOX(버려도 되는 퀴즈 편집용) 과목의 course_id. 목록에서 제목으로 검색하면 최근 다른 팀이
# 만든 과목이 계속 쌓이면서 앞쪽 페이지에서 SANDBOX가 밀려나 못 찾는 문제가 있어(2026-07-20 확인),
# 목록 검색 대신 알려진 course_id를 직접 조회한다. EDU_SANDBOX_COURSE_ID 환경변수로 덮어쓸 수 있다.
EDU_SANDBOX_COURSE_ID = int(os.getenv("EDU_SANDBOX_COURSE_ID", "89"))


@pytest.fixture(scope="session")
def access_token() -> str:
    """course_edu 전용 override: 공용 .env와 무관하게 항상 dev 교육자 계정으로 로그인한다.

    루트 conftest.py의 access_token을 이 파일에서 같은 이름으로 재정의해서,
    이를 참조하는 student_user_id 등 다른 공용 fixture도 자동으로 이 토큰을 쓰게 된다.
    """
    try:
        token = edu_login(EDU_ELICE_ID, EDU_ELICE_PW)
    except RuntimeError as exc:
        pytest.fail(f"교육자 계정 로그인 실패({EDU_ELICE_ID}): {exc}")
    logger.info("[준비] 교육자(educator) 토큰 발급 완료: %s", EDU_ELICE_ID)
    return token


@pytest.fixture(scope="session")
def api_client(requests_session, access_token: str) -> ApiClient:
    """course_edu 전용 override: 교육자 토큰 + academy org 헤더 고정."""
    return ApiClient(requests_session, settings, access_token=access_token, org_name_short=EDU_ORG_NAME_SHORT)


@pytest.fixture(scope="session")
def api_client_factory(requests_session):
    """course_edu 전용 override: org 기본값을 academy로 고정한 client factory.

    (인증 네거티브 테스트가 access_token만 깨뜨려도 org 헤더/경로는 academy를 가리키게 한다)
    """
    def create(
        *,
        access_token: str | None = None,
        org_name_short: str | None = None,
        include_auth: bool = True,
        include_org: bool = True,
    ) -> ApiClient:
        return ApiClient(
            requests_session,
            settings,
            access_token=access_token,
            org_name_short=org_name_short if org_name_short is not None else EDU_ORG_NAME_SHORT,
            include_auth=include_auth,
            include_org=include_org,
        )

    return create


def _user_id_from_token(access_token: str) -> int | None:
    """JWT access_token에서 사용자 id(_id)를 추출한다. 실패하면 None."""
    try:
        payload_b64 = access_token.split(".")[1]
        padded_payload = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload))
    except (IndexError, ValueError, json.JSONDecodeError):
        return None
    return payload.get("_id")


@pytest.fixture(scope="session")
def classroom_id(api_client: ApiClient, access_token: str) -> str:
    """course_edu 전용 override: 항상 dev classroom-api(EDU_API_BASE_URL)에서 찾는다.

    루트 conftest.py의 classroom_id는 공용 settings.API_BASE_URL을 직접 참조해서,
    이 값이 (course처럼) 운영으로 바뀌면 dev 토큰이 거부된다. 여기서는 dev host를 고정하고,
    루트의 dev 분기 로직(로그인한 교육자 계정 기준으로 열려있고 과목이 있는 classroom 탐색)만 재사용한다.
    """
    user_id = _user_id_from_token(access_token)
    if user_id is None:
        pytest.skip("dev classroom 조회에 필요한 사용자 id를 토큰에서 찾지 못했습니다.")

    params = {
        "skip": 0,
        "count": 20,
        "filter_opened_list": "true",
        "filter_name": "%%",
        "filter_member_account_id": user_id,
    }
    response = api_client.get(EDU_API_BASE_URL, "/classroom", params=params)
    assert response.status_code == 200, f"classroom list: status={response.status_code}, body={response.text[:300]}"

    classrooms = response.json()
    target = next(
        (item for item in classrooms if item.get("opened", True) and item.get("course_count", 0) > 0),
        None,
    )
    if target is None:
        names = ", ".join(item.get("name", "<이름 없음>") for item in classrooms)
        pytest.skip(f"dev classroom 목록에서 조건에 맞는 classroom을 찾지 못했습니다. 조회된 classroom: {names}")

    logger.info("[준비] classroom_id 확보: %s -> %s", target["name"], target["id"])
    return target["id"]


@pytest.fixture(scope="session")
def learner_access_token() -> str:
    """학생(le01) 계정으로 로그인해 access_token을 발급받는다. (권한 경계 테스트 전용)"""
    try:
        token = edu_login(LEARNER_ID, LEARNER_PW)
    except RuntimeError as exc:
        pytest.skip(f"학생 계정 로그인 실패({LEARNER_ID}): {exc}")
    logger.info("[준비] 학생(learner) 토큰 발급 완료: %s", LEARNER_ID)
    return token


@pytest.fixture(scope="session")
def learner_api_client(requests_session, learner_access_token) -> ApiClient:
    """학생 토큰 + academy org 헤더가 붙은 client.

    인증은 정상(학생 토큰)이지만 교육자 전용 API에는 권한이 없어야 한다.
    (api_client_factory의 '깨진 토큰'과 달리, 여기선 유효한 학생 토큰을 쓴다.)
    """
    return ApiClient(requests_session, settings, access_token=learner_access_token, org_name_short=EDU_ORG_NAME_SHORT)


@pytest.fixture(scope="session")
def course_id(api_client) -> int:
    """교육자 과목 목록에서 강의(lecture)가 있는 과목의 course_id를 자동으로 찾습니다."""
    body = CourseEduPage(api_client).get_course_list(offset=0, count=30).json()
    courses = body.get("courses", [])
    if not courses:
        pytest.skip("교육자 과목 목록이 비어 있습니다. (org/course/list)")

    for c in courses:
        cid = c.get("course_id") or c.get("id")
        lecture_count = CourseEduPage(api_client).get_lecture_list(course_id=cid, offset=0, count=5).json().get("lecture_count", 0)
        if lecture_count > 0:
            logger.info("[준비] course_id 확보(콘텐츠 있음): %s -> %s (lecture_count=%s)",
                        c.get("title"), cid, lecture_count)
            return cid

    fallback = courses[0].get("course_id") or courses[0].get("id")
    logger.info("[준비] 콘텐츠 과목 못 찾음 -> 첫 과목 사용: %s", fallback)
    return fallback


@pytest.fixture(scope="session")
def editable_lecture(api_client) -> tuple[int, dict]:
    """편집-복원 테스트용 Normal(type 0) 수업을 찾아 (course_id, lecture dict)를 반환합니다.

    Test 타입(type 1)은 test_* 필수 필드가 많아 편집 payload가 복잡하므로 Normal만 씁니다.
    """
    body = CourseEduPage(api_client).get_course_list(offset=0, count=30).json()
    for c in body.get("courses", []):
        cid = c.get("course_id") or c.get("id")
        lectures = CourseEduPage(api_client).get_lecture_list(course_id=cid, offset=0, count=30).json().get("lectures", [])
        target = next((lec for lec in lectures if lec.get("lecture_type") == 0), None)
        if target is not None:
            logger.info("[준비] 편집 대상 수업 확보: course_id=%s, lecture_id=%s, title=%r",
                        cid, target.get("id"), target.get("title"))
            return cid, target

    pytest.skip("편집 가능한 Normal(type 0) 수업을 찾지 못했습니다.")


@pytest.fixture(scope="session")
def section_id(api_client, course_id) -> int:
    """course의 첫 번째 섹션(course_section_id)을 반환합니다."""
    sections = CourseEduPage(api_client).get_section_list(course_id=course_id, offset=0, count=20).json().get("course_sections", [])
    if not sections:
        pytest.skip("과목에 섹션이 없습니다.")
    sec_id = sections[0].get("id") or sections[0].get("course_section_id")
    logger.info("[준비] section_id 확보: %s", sec_id)
    return sec_id


@pytest.fixture(scope="session")
def course_info_id(api_client, course_id) -> int:
    """course/get 응답에서 course_info_id를 추출합니다."""
    course = CourseEduPage(api_client).get_course_detail(course_id=course_id).json().get("course", {})
    info_id = course.get("course_info_id")
    if info_id is None:
        pytest.skip("course_info_id를 찾지 못했습니다.")
    logger.info("[준비] course_info_id 확보: %s", info_id)
    return info_id


@pytest.fixture(scope="session")
def lecture_id(api_client, course_id) -> int:
    """course의 첫 번째 강의(lecture_id)를 반환합니다."""
    lectures = CourseEduPage(api_client).get_lecture_list(course_id=course_id, offset=0, count=30).json().get("lectures", [])
    if not lectures:
        pytest.skip("과목에 강의가 없습니다.")
    lec_id = lectures[0].get("id") or lectures[0].get("lecture_id")
    logger.info("[준비] lecture_id 확보: %s", lec_id)
    return lec_id


@pytest.fixture(scope="session")
def sandbox_quiz(api_client) -> dict:
    """SANDBOX(버려도 되는) 과목에서 퀴즈(material_type 5) 자료를 찾아
    (material_quiz_id, lecture_id, lecture_page_id)를 반환합니다.

    퀴즈 편집은 문항 내용까지 덮으므로, 실제 과목이 아닌 SANDBOX로 범위를 제한합니다.

    목록(list)에서 제목으로 검색하지 않고 EDU_SANDBOX_COURSE_ID를 바로 조회한다.
    """
    course = CourseEduPage(api_client).get_course_detail(course_id=EDU_SANDBOX_COURSE_ID).json().get("course", {})
    if "SANDBOX" not in (course.get("title") or ""):
        pytest.skip(f"SANDBOX 과목(course_id={EDU_SANDBOX_COURSE_ID})을 찾지 못했습니다.")
    cid = EDU_SANDBOX_COURSE_ID

    sections = CourseEduPage(api_client).get_section_list(course_id=cid, offset=0, count=20).json().get("course_sections", [])
    lectures = CourseEduPage(api_client).get_lecture_list(course_id=cid, offset=0, count=30).json().get("lectures", [])
    for lec in lectures:
        lec_id = lec.get("id")
        for sec in sections:
            body = CourseEduPage(api_client).get_lecture_detail(lecture_id=lec_id, course_section_id=sec.get("id")).json()
            if body.get("_result", {}).get("status") != "ok":
                continue
            lecture = body.get("lecture", {})
            for page_key in ("main_lecture_pages", "sub_lecture_pages"):
                for page in lecture.get(page_key) or []:
                    if page.get("material_type") == 5:  # 5 = quiz
                        info = {
                            "material_quiz_id": page.get("material_id"),
                            "lecture_id": lec_id,
                            "lecture_page_id": page.get("id"),
                        }
                        logger.info("[준비] SANDBOX 퀴즈 확보: %s", info)
                        return info

    pytest.skip("SANDBOX에서 퀴즈(material_type 5) 자료를 찾지 못했습니다.")
