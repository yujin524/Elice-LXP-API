"""공통 Allure 메타데이터 생성 규칙 단위 테스트."""

from pathlib import Path
from types import SimpleNamespace

from tests.api.plugins.allure_metadata import _set_allure_title, build_allure_metadata


class FakeItem:
    """pytest Item에서 메타데이터 생성에 필요한 속성만 흉내 냅니다."""

    def __init__(
        self,
        path: str,
        tc_info: dict[str, str] | None,
        *,
        name: str = "test_case",
        case_id: str | None = None,
    ) -> None:
        self.path = Path(path)
        self.name = name
        if tc_info is not None:
            self._marker = SimpleNamespace(kwargs=tc_info)
        else:
            self._marker = None
        if case_id is not None:
            self.callspec = SimpleNamespace(id=case_id)

    def get_closest_marker(self, marker_name: str):
        assert marker_name == "tc"
        return self._marker


def test_build_metadata_uses_api_path_and_tc_marker() -> None:
    """경로와 TC 마커가 Suites 계층·표시 이름·설명으로 변환됩니다."""
    item = FakeItem(
        "tests/api/schedule/validation/test_get_schedule.py",
        {
            "id": "API_CS_003",
            "group": "Validation",
            "title": "classroom_id 누락",
            "expected": "HTTP 422",
        },
        case_id="API_CS_003",
    )

    metadata = build_allure_metadata(item)

    assert metadata == {
        "parent_suite": "Schedule",
        "suite": "Validation",
        "sub_suite": "get_schedule",
        "epic": "API Automation",
        "feature": "Schedule",
        "story": "Validation",
        "title": "[API_CS_003] classroom_id 누락",
        "tc_id": "API_CS_003",
        "description": (
            "TC ID: API_CS_003\n\n"
            "Expected: HTTP 422\n\n"
            "Source: tests/api/schedule/validation/test_get_schedule.py"
        ),
    }


def test_build_metadata_appends_distinct_parameter_case_id() -> None:
    """하나의 TC가 여러 인증 조건을 가지면 parameter ID로 결과를 구분합니다."""
    item = FakeItem(
        "tests/api/board/authentication/test_get_board_article.py",
        {
            "id": "API_BA_017",
            "group": "Authentication",
            "title": "인증 실패",
            "expected": "HTTP 401",
        },
        case_id="empty_token",
    )

    metadata = build_allure_metadata(item)

    assert metadata is not None
    assert metadata["title"] == "[API_BA_017] 인증 실패 · empty_token"
    assert metadata["parent_suite"] == "Board"
    assert metadata["suite"] == "Authentication"
    assert metadata["sub_suite"] == "get_board_article"


def test_build_metadata_ignores_unit_test() -> None:
    """API 외 테스트의 기존 Allure 표시는 변경하지 않습니다."""
    item = FakeItem(
        "tests/unit/test_logger.py",
        {
            "id": "UNIT_001",
            "group": "Unit",
            "title": "로그 마스킹",
            "expected": "민감정보 제거",
        },
    )

    assert build_allure_metadata(item) is None


def test_build_metadata_ignores_api_test_without_tc_marker() -> None:
    """TC 마커가 없는 API 보조 테스트에는 임의 메타데이터를 만들지 않습니다."""
    item = FakeItem(
        "tests/api/common/test_helper.py",
        None,
    )

    assert build_allure_metadata(item) is None


def test_set_allure_title_supports_class_test_method() -> None:
    """클래스 테스트의 바인딩 메서드에도 setup 오류 없이 제목을 설정합니다."""

    class ClassBasedTest:
        def test_case(self) -> None:
            pass

    item = SimpleNamespace(obj=ClassBasedTest().test_case)

    _set_allure_title(item, "[EDU_B_001] 강의 수정 권한 검증")

    assert item.obj.__allure_display_name__ == "[EDU_B_001] 강의 수정 권한 검증"
