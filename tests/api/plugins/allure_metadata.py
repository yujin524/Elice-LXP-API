"""API 테스트의 Allure 분류와 표시 이름을 한곳에서 관리합니다.

각 테스트 파일에 ``@allure.*`` 데코레이터를 반복하지 않고, 기존
``pytest.mark.tc``와 파일 경로를 기준으로 Allure 메타데이터를 만듭니다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import allure


DOMAIN_LABELS = {
    "board": "Board",
    "classroom": "Classroom",
    "classroom_edu": "Classroom Management",
    "course": "Course",
    "course_edu": "Course Management",
    "schedule": "Schedule",
}

TEST_TYPE_LABELS = {
    "positive": "Positive",
    "validation": "Validation",
    "authentication": "Authentication",
    "authorization": "Authorization",
    "boundary": "Boundary",
    "scenario": "Scenario",
}


def _api_path_parts(path: Path) -> tuple[str, str, str, str] | None:
    """경로에서 domain, test type, target, 표시용 source를 추출합니다."""
    parts = path.as_posix().split("/")

    try:
        tests_index = parts.index("tests")
    except ValueError:
        return None

    api_parts = parts[tests_index:]
    if len(api_parts) < 5 or api_parts[1] != "api":
        return None

    domain = api_parts[2]
    test_type = api_parts[3]
    test_file = Path(api_parts[-1])
    target = test_file.stem.removeprefix("test_")
    source = "/".join(api_parts)
    return domain, test_type, target, source


def _case_id(item: Any, tc_id: str) -> str | None:
    """TC ID와 구분되는 pytest parameter ID만 반환합니다."""
    callspec = getattr(item, "callspec", None)
    case_id = str(getattr(callspec, "id", "") or "").strip()

    if not case_id or case_id == tc_id or case_id.startswith(tc_id):
        return None
    return case_id


def build_allure_metadata(item: Any) -> dict[str, str] | None:
    """pytest item에서 Allure에 전달할 메타데이터를 만듭니다.

    API 경로가 아니거나 ``tc`` 마커가 없는 테스트는 기존 표시를 유지하기
    위해 ``None``을 반환합니다.
    """
    path_info = _api_path_parts(Path(item.path))
    tc_marker = item.get_closest_marker("tc")

    if path_info is None or tc_marker is None:
        return None

    domain, test_type, target, source = path_info
    tc_info = tc_marker.kwargs
    tc_id = str(tc_info.get("id") or "").strip()
    title = str(tc_info.get("title") or getattr(item, "name", "")).strip()
    group = str(tc_info.get("group") or TEST_TYPE_LABELS.get(test_type, test_type)).strip()
    expected = str(tc_info.get("expected") or "").strip()

    display_title = f"[{tc_id}] {title}" if tc_id else title
    case_id = _case_id(item, tc_id)
    if case_id:
        display_title = f"{display_title} · {case_id}"

    description_lines = []
    if tc_id:
        description_lines.append(f"TC ID: {tc_id}")
    if expected:
        description_lines.append(f"Expected: {expected}")
    description_lines.append(f"Source: {source}")

    return {
        "parent_suite": DOMAIN_LABELS.get(domain, domain.replace("_", " ").title()),
        "suite": TEST_TYPE_LABELS.get(test_type, test_type.title()),
        "sub_suite": target,
        "epic": "API Automation",
        "feature": DOMAIN_LABELS.get(domain, domain.replace("_", " ").title()),
        "story": group,
        "title": display_title,
        "tc_id": tc_id,
        "description": "\n\n".join(description_lines),
    }


def _set_allure_title(item: Any, title: str) -> None:
    """일반 함수와 클래스 메서드 모두에 Allure 제목을 설정합니다.

    클래스 기반 테스트의 ``item.obj``는 속성을 직접 추가할 수 없는 바인딩
    메서드입니다. 이 경우 실제 함수인 ``__func__``에 제목을 기록합니다.
    """
    title_target = getattr(item.obj, "__func__", item.obj)
    allure.title(title)(title_target)


def apply_allure_metadata(item: Any) -> None:
    """계산된 메타데이터를 현재 Allure 테스트 결과에 반영합니다."""
    metadata = build_allure_metadata(item)
    if metadata is None:
        return

    # Allure listener는 setup 종료 시 함수의 제목과 description 마커를 다시 읽습니다.
    # 이 두 값은 동적 API만 사용하면 setup 단계에서 skip된 결과에 남지 않으므로,
    # listener가 읽는 원본에도 함께 기록합니다.
    _set_allure_title(item, metadata["title"])
    item.add_marker(allure.description(metadata["description"]))

    allure.dynamic.parent_suite(metadata["parent_suite"])
    allure.dynamic.suite(metadata["suite"])
    allure.dynamic.sub_suite(metadata["sub_suite"])
    allure.dynamic.epic(metadata["epic"])
    allure.dynamic.feature(metadata["feature"])
    allure.dynamic.story(metadata["story"])
    allure.dynamic.title(metadata["title"])
    allure.dynamic.description(metadata["description"])

    if metadata["tc_id"]:
        allure.dynamic.label("tc_id", metadata["tc_id"])
