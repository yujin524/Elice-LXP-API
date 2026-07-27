"""교육자(강사) 전용 학습 과목 API 요청 클래스. (dev 서버)

과목 편집 / 수업 관리 화면에서 호출하는 `/org/{org}/...` (REST_BASE_URL) API들입니다.
이 계열은 HTTP 200이라도 성공/실패는 응답 body의 `_result`에 담기므로,
검증은 tests/api/common/assertions.py의 assert_rest_result_ok / assert_rest_result_failed 를 씁니다.

write(POST/DELETE) 계열은 **multipart/form-data**로 보내야 한다(브라우저 캡처로 확인).
requests에서는 files= 로 넘기면 multipart로 인코딩된다.

주의: write 계열은 데이터를 실제로 바꾼다. 테스트는 반드시 "편집 -> 확인 -> 복원" 또는
"생성 -> 확인 -> 삭제" 처럼 되돌리는 형태로 사용할 것.

파라미터는 [LXP]API_spec 명세서 기준입니다. 대부분의 list API는 offset·count가 필수입니다.
"""

from __future__ import annotations
import json
import os
from typing import Any
import requests
from config import settings
from utils.api_client import ApiClient
from utils.logger import get_logger, log_direct_request, log_direct_response, redact_text


logger = get_logger(__name__)

# course_edu(교육자)는 항상 dev 서버·academy org를 대상으로 한다.
# 공용 settings.REST_BASE_URL / DASHBOARD_BASE_URL / ELICE_ORG_NAME_SHORT는 학생(course)
# 도메인과 공유되는 값이라 다른 팀 작업으로 바뀔 수 있으므로(예: REST_BASE_URL이
# dev-qatrack-api-rest.* 로 바뀌면 /org/ 엔드포인트가 400을 반환하는 문제가 실제로 있었음),
# 여기서는 settings의 그 값들에 기대지 않고 알려진 정상 host/org를 직접 기본값으로 둔다.
# EDU_REST_BASE_URL만 다른 _BASE_URL들처럼 config/settings.py에서 공통 관리한다
# (그래도 이름은 별도라 REST_BASE_URL이 바뀌어도 영향받지 않는다).
# 그래도 필요하면 EDU_* 환경변수로 언제든 덮어쓸 수 있다.
EDU_REST_BASE_URL = settings.EDU_REST_BASE_URL
EDU_DASHBOARD_BASE_URL = os.getenv(
    "EDU_DASHBOARD_BASE_URL", "https://dev-qatrack-dashboard-api.dev.elicer.io"
).rstrip("/")
# 클래스룸(과목 목록/추가/삭제/순서변경) classroom-api dev 호스트. 공용 settings.API_BASE_URL이
# (course처럼) 운영으로 바뀌면 dev 토큰이 거부되므로 이것도 분리한다.
EDU_API_BASE_URL = os.getenv("EDU_API_BASE_URL", "https://dev-qatrack-classroom-api.dev.elicer.io").rstrip("/")
EDU_ORG_NAME_SHORT = os.getenv("EDU_ORG_NAME_SHORT", "academy")

# 로그인용 dev 계정 서버. 공용 settings.AUTH_URL이 (course처럼) 운영으로 바뀌어도
# course_edu의 로그인은 항상 이 dev 계정 서버를 쓰도록 분리한다.
EDU_AUTH_URL = os.getenv("EDU_AUTH_URL", "https://dev-qatrack-account-api.dev.elicer.io").rstrip("/")


def edu_login(login_id: str, password: str) -> str:
    """course_edu 전용 로그인. 공용 utils/auth_token.get_token(settings.AUTH_URL 고정)과
    별개로, 항상 EDU_AUTH_URL(dev 계정 서버)로 로그인해 access_token을 발급받는다.

    공통 get_token()은 AUTH_URL을 사용하므로, 별도 EDU_AUTH_URL이 필요한 이 로그인만
    requests 호출을 직접 수행하고 공통 Logger 형식으로 요청/응답을 기록한다.
    """
    login_url = f"{EDU_AUTH_URL}/login/pw"
    request_json = {"login_id": login_id, "password": password}
    log_direct_request(logger, "POST", login_url, json=request_json)
    try:
        response = requests.post(
            login_url,
            json=request_json,
            timeout=10,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"교육자 로그인 요청 실패: {redact_text(exc)}") from exc

    log_direct_response(logger, response)

    if response.status_code != 200:
        raise RuntimeError(f"교육자 로그인 실패 (status={response.status_code}): {response.text}")

    try:
        body = response.json()
    except ValueError as exc:
        raise RuntimeError(f"교육자 로그인 응답 JSON 파싱 실패: {response.text}") from exc

    access_token = body.get("access_token") if isinstance(body, dict) else None
    if not access_token:
        raise RuntimeError(f"응답에 access_token이 없습니다: {body}")

    return access_token


def _multipart(fields: dict[str, Any]) -> dict[str, tuple[None, str]]:
    """dict를 requests의 multipart/form-data 형식(files=)으로 변환."""
    return {key: (None, str(value)) for key, value in fields.items()}


class CourseEduPage:
    """교육자(강사)용 과목/수업 관리 API 요청을 담당합니다."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def _org_path(self, path: str) -> str:
        return f"/org/{EDU_ORG_NAME_SHORT}/{path}"

    # =========================================================
    # 학생별 학습현황 (dashboard)
    # =========================================================

    def get_student_course_progress(self, *, student_user_id: int, classroom_id: str, offset: int = 0, count: int = 10):
        """학생별 과목 학습현황 조회 (dashboard /student/{id}/course).

        교육자 대시보드에서 특정 학생의 과목별 진행 현황을 본다. dashboard 계열이라 HTTP 상태로 판정.
        """
        return self.client.get(
            EDU_DASHBOARD_BASE_URL,
            f"/student/{student_user_id}/course",
            params={"classroom_id": classroom_id, "offset": offset, "count": count},
        )

    # =========================================================
    # 과목 편집 (org/course)
    # =========================================================

    def get_course_list(self, *, offset: int = 0, count: int = 20):
        """교육자 과목 목록 조회 (org/course/list)."""
        return self.client.get(EDU_REST_BASE_URL, self._org_path("course/list/"), params={"offset": offset, "count": count})

    def get_course_detail(self, *, course_id: int):
        """과목 상세 조회 - 편집 화면 로드 (org/course/get)."""
        return self.client.get(EDU_REST_BASE_URL, self._org_path("course/get/"), params={"course_id": course_id})

    def get_section_list(self, *, course_id: int, offset: int = 0, count: int = 20):
        """커리큘럼(섹션) 목록 조회 (org/course/section/list)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/section/list/"),
            params={"course_id": course_id, "offset": offset, "count": count},
        )

    def get_course_user_list(
        self,
        *,
        course_id: int,
        is_for_tutoring: bool = False,
        offset: int = 0,
        count: int = 20,
    ):
        """수강생 목록 조회 (org/course/user/list). is_for_tutoring 필수(문자열 'true'/'false')."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/user/list/"),
            params={
                "course_id": course_id,
                "is_for_tutoring": "true" if is_for_tutoring else "false",
                "offset": offset,
                "count": count,
            },
        )

    def get_notice_list(self, *, course_id: int, offset: int = 0, count: int = 20):
        """과목 공지 목록 조회 (org/course/notice/list)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/notice/list/"),
            params={"course_id": course_id, "offset": offset, "count": count},
        )

    def get_completion_list(self, *, offset: int = 0, count: int = 20):
        """수료 현황 목록 조회 (org/course/completion/list). course_id 불필요(조직 단위)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/completion/list/"),
            params={"offset": offset, "count": count},
        )

    def get_info_review_list(self, *, course_info_id: int, offset: int = 0, count: int = 20):
        """수강 후기 목록 조회 (org/course/info/review/list). course_info_id 필수."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/info/review/list/"),
            params={"course_info_id": course_info_id, "offset": offset, "count": count},
        )

    def edit_section(self, *, course_id: int, name: str, course_section_id: int | None = None):
        """커리큘럼 섹션 추가/편집 (org/course/section/edit, multipart).

        course_section_id 없으면 생성, 있으면 편집. 이름만 바꾸므로 편집-복원이 안전하다.
        """
        fields: dict[str, Any] = {"course_id": course_id, "name": name}
        if course_section_id is not None:
            fields["course_section_id"] = course_section_id
        path = self._org_path("course/section/edit/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def add_section_schedules(self, *, course_section_id: int, section_schedule_list):
        """수업 일정 일괄 추가 (org/course/section/schedule/add/bulk, multipart).

        section_schedule_list: [{"begin_datetime": <epoch_ms>, "end_datetime": <epoch_ms>}, ...]
        ⚠️ 생성 계열. 실제로 일정이 추가되므로 positive에는 삭제가 필요. boundary/validation 용도로 쓸 것.
        """
        fields = {
            "course_section_id": course_section_id,
            "section_schedule_list": json.dumps(section_schedule_list),
        }
        path = self._org_path("course/section/schedule/add/bulk/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def get_section_schedule_list(self, *, course_section_id: int, offset: int = 0, count: int = 20):
        """수업 일정 목록 조회 (org/course/section/schedule/list)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("course/section/schedule/list/"),
            params={"course_section_id": course_section_id, "offset": offset, "count": count},
        )

    def add_section_users(self, *, course_section_id: int, user_ident_list: list[str]):
        """섹션(수업)에 수강생 추가 (org/course/section/user/add/by_user_ident, multipart).

        user_ident_list: 이메일 등 식별자 리스트.
        ⚠️ 실제로 수강생을 추가하므로 positive에는 정리가 필요. boundary/validation 용도로 쓸 것.
        """
        fields = {
            "course_section_id": course_section_id,
            "user_ident_list": json.dumps(user_ident_list),
        }
        path = self._org_path("course/section/user/add/by_user_ident/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    # =========================================================
    # 수업 관리 (org/lecture)
    # =========================================================

    def get_lecture_list(self, *, course_id: int, offset: int = 0, count: int = 20):
        """강의 목록 조회 (org/lecture/list)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("lecture/list/"),
            params={"course_id": course_id, "offset": offset, "count": count},
        )

    def get_lecture_detail(self, *, lecture_id: int, course_section_id: int):
        """강의(수업) 상세 조회 (org/lecture/get). lecture_id + course_section_id 필수."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("lecture/get/"),
            params={"lecture_id": lecture_id, "course_section_id": course_section_id},
        )

    def edit_lecture(
        self,
        *,
        course_id: int,
        title: str,
        description: str = "",
        lecture_type: int = 0,
        is_opened: bool = False,
        is_preview: bool = False,
        lecture_id: int | None = None,
    ):
        """수업(강의) 추가/편집 (org/lecture/edit, multipart).

        lecture_id 없으면 생성, 있으면 편집(upsert). lecture_type 0=Normal, 1=Test, 2=Recommend.
        """
        fields: dict[str, Any] = {
            "course_id": course_id,
            "lecture_type": lecture_type,
            "title": title,
            "description": description,
            "is_opened": "true" if is_opened else "false",
            "is_preview": "true" if is_preview else "false",
        }
        if lecture_id is not None:
            fields["lecture_id"] = lecture_id

        path = self._org_path("lecture/edit/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def set_lecture_schedule(
        self,
        *,
        lecture_id: int,
        open_schedule_datetime: int,
        close_schedule_datetime: int,
    ):
        """수업 공개/마감 일정 설정 (org/lecture/schedule, multipart).

        ⚠️ 기존 수업의 일정을 변경한다. boundary(학생 차단) / validation(없는 lecture_id) 용도로 쓸 것.
        """
        fields = {
            "lecture_id": lecture_id,
            "open_schedule_datetime": open_schedule_datetime,
            "close_schedule_datetime": close_schedule_datetime,
        }
        path = self._org_path("lecture/schedule/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def create_lectureroom(
        self,
        *,
        course_id: int,
        course_section_id: int,
        title: str,
        purpose: int = 10,
        auto_recording: bool = False,
    ):
        """라이브 강의실 생성/편집 (org/course/lectureroom/edit, multipart).

        ⚠️ 생성 계열. 실제로 강의실이 만들어지므로 positive에는 삭제가 필요. boundary/validation 용도로 쓸 것.
        """
        fields = {
            "course_id": course_id,
            "title": title,
            "purpose": purpose,
            "default_publish_locked_device_names": "[]",
            "course_section_id": course_section_id,
            "auto_recording": "true" if auto_recording else "false",
            "cheat_info": "{}",
        }
        path = self._org_path("course/lectureroom/edit/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def edit_material_assignment(
        self,
        *,
        lecture_id: int,
        title: str,
        lecture_page_id: str = "undefined",
        description: str = "",
        close_datetime: int | None = None,
        is_opened: bool = False,
        is_resubmit_enabled: bool = False,
    ):
        """과제 자료 추가/편집 (org/material_assignment/edit, multipart).

        ⚠️ 생성/변경 계열. 실제로 과제가 만들어지므로 positive에는 정리가 필요.
        boundary(학생 차단) / validation(없는 lecture_id) 용도로 쓸 것.
        """
        fields: dict[str, Any] = {
            "is_opened": "true" if is_opened else "false",
            "lecture_id": lecture_id,
            "lecture_page_id": lecture_page_id,
            "title": title,
            "description": description,
            "locator_types": "0",
            "instruction_content": "",
            "solution_content": "",
            "is_for_stats": "true",
            "is_display_score": "false",
            "is_resubmit_enabled": "true" if is_resubmit_enabled else "false",
        }
        if close_datetime is not None:
            fields["close_datetime"] = close_datetime
        path = self._org_path("material_assignment/edit/")
        return self.client.post(EDU_REST_BASE_URL, path, files=_multipart(fields))

    def get_material_quiz(self, *, material_quiz_id: int):
        """퀴즈 수업자료 상세 조회 (org/material_quiz/get)."""
        return self.client.get(
            EDU_REST_BASE_URL,
            self._org_path("material_quiz/get/"),
            params={"material_quiz_id": material_quiz_id},
        )

    def edit_material_quiz(
        self,
        *,
        material_quiz_id: int,
        lecture_id: int,
        lecture_page_id: int,
        title: str,
    ):
        """퀴즈 수업자료 편집 (org/material_quiz/edit, multipart).

        주의: 퀴즈 편집 payload는 30개+ 필드에 문항 내용까지 포함된다. 아래 값은 브라우저 캡처를
        기반으로 한 **고정 템플릿**이라, 이 함수로 편집하면 title 외 문항 내용도 템플릿 값으로 덮인다.
        따라서 **버려도 되는 SANDBOX 테스트 퀴즈에만** 사용할 것 (real 퀴즈에는 쓰지 말 것).
        """
        fields = [
            ("is_opened", "true"),
            ("id", str(material_quiz_id)),
            ("title", title),
            ("taglist", "[]"),
            ("description", ""),
            ("solution_content", ""),
            ("difficulty_type", "10"),
            ("is_auto_grade", "true"),
            ("option_type", "0"),
            ("options", "[object Object]"),
            ("options", "[object Object]"),
            ("options_default", '[{"title":"","content":"Correct"},{"title":"","content":"Incorrect"}]'),
            ("options_set_enabled", "false"),
            ("user_quiz_options_set_enabled", "false"),
            ("answer_info", "0"),
            ("answer_info_default", "[0]"),
            ("answer_text_type", "1"),
            ("correct_option_count", "1"),
            ("question_title", "Untitled Quiz"),
            ("question_description", "<p>QA test</p>"),
            ("explanation_info", '{"is_enabled":false,"value":""}'),
            ("is_responded", "true"),
            ("is_someone_responded", "true"),
            ("is_enrolled_student_responded", "false"),
            ("last_quiz_response_id", "0"),
            ("material_quiz_id", str(material_quiz_id)),
            ("lecture_id", str(lecture_id)),
            ("lecture_page_id", str(lecture_page_id)),
            ("locator_types", "0"),
            ("instruction_content", ""),
            ("is_for_stats", "true"),
            ("is_display_score", "false"),
        ]
        files = [(name, (None, value)) for name, value in fields]
        path = self._org_path("material_quiz/edit/")
        return self.client.post(EDU_REST_BASE_URL, path, files=files)

    # =========================================================
    # 클래스룸 과목 순서 (classroom-api, HTTP status 판정 · 동기)
    # =========================================================

    def list_classroom_courses(self, *, classroom_id: str, offset: int = 0, count: int = 80):
        """클래스룸 과목 목록 조회 (classroom-api, 단일 페이지). 리스트 순서가 곧 노출 순서."""
        return self.client.get(
            EDU_API_BASE_URL,
            f"/classroom/{classroom_id}/course",
            params={"skip": offset, "count": count},
        )

    def list_all_classroom_courses(self, *, classroom_id: str) -> list[dict]:
        """클래스룸의 전체 과목을 페이징으로 끝까지 모아서 반환한다.

        reorder API는 보낸 course_ids가 클래스룸의 전체 집합과 정확히 일치해야 하는데
        (일부만 보내면 invalid_params/mismatch로 거부됨), 과목이 계속 늘어나면서 고정
        count=80 한 페이지만 읽던 기존 방식은 뒤쪽 과목이 잘려 순서 변경이 실패했다
        (2026-07-23 확인: 실제 100개인데 80개만 읽어서 발생). count는 서버가 한 번에
        최대 100개까지만 주므로, 100개 단위로 끝까지 순회한다.
        """
        courses: list[dict] = []
        offset = 0
        page_size = 100
        while True:
            resp = self.list_classroom_courses(classroom_id=classroom_id, offset=offset, count=page_size)
            assert resp.status_code == 200, f"클래스룸 과목 목록 조회 실패: status={resp.status_code}"
            page = resp.json()
            courses.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        return courses

    def reorder_courses(self, *, classroom_id: str, course_ids: list[int]):
        """클래스룸 과목 순서 변경 (classroom-api).

        전체 course_id를 원하는 순서로 보낸다. REST(_result)가 아니라 HTTP 상태 코드로 판정한다.
        """
        return self.client.post(
            EDU_API_BASE_URL,
            f"/classroom/{classroom_id}/course/reorder",
            json={"course_ids": course_ids},
        )

    def add_courses_bulk(self, *, classroom_id: str, original_course_ids: list[int]):
        """클래스에 과목 복제 추가 (classroom-api v2, **async → task_id 반환**).

        original_course_ids: 카탈로그 원본 course_id 리스트. 응답의 task_id로 백그라운드 처리된다.
        ⚠️ 실제 과목이 생성되므로, 반드시 목록 폴링으로 새 course_id를 확보하고 delete_course로 정리할 것.
        """
        return self.client.post(
            EDU_API_BASE_URL,
            f"/v2/classroom/{classroom_id}/course/bulk",
            json={"original_course_ids": list(original_course_ids)},
        )

    def delete_course(self, *, classroom_id: str, course_id: int):
        """클래스룸 과목 삭제 (classroom-api, DELETE).

        ⚠️ 파괴적 작업. 권한 경계 테스트에서 **없는 course_id로 '거부되는지'만** 확인하는 용도로 쓸 것.
        (실제 존재하는 course_id로 호출하면 만에 하나 삭제될 수 있으므로 금지)
        """
        return self.client.delete(
            EDU_API_BASE_URL,
            f"/classroom/{classroom_id}/course/{course_id}",
        )
