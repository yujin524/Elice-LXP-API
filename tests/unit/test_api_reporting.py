# api_reporting plugin 단위 테스트

from types import SimpleNamespace
import pytest
from tests.api.plugins import api_reporting
from tests.api.plugins.api_reporting import _summary_group


@pytest.fixture(autouse=True)
def clear_api_reporting_state():
    saved_results = list(api_reporting.SUMMARY_RESULTS)
    saved_recorded_nodeids = set(api_reporting.RECORDED_NODEIDS)
    saved_tc_metadata = dict(api_reporting.TC_METADATA_BY_NODEID)
    api_reporting.SUMMARY_RESULTS.clear()
    api_reporting.RECORDED_NODEIDS.clear()
    api_reporting.TC_METADATA_BY_NODEID.clear()
    yield
    api_reporting.SUMMARY_RESULTS.clear()
    api_reporting.SUMMARY_RESULTS.extend(saved_results)
    api_reporting.RECORDED_NODEIDS.clear()
    api_reporting.RECORDED_NODEIDS.update(saved_recorded_nodeids)
    api_reporting.TC_METADATA_BY_NODEID.clear()
    api_reporting.TC_METADATA_BY_NODEID.update(saved_tc_metadata)


def test_summary_group_maps_specific_case_groups_to_report_groups() -> None:
    """테스트 케이스의 세부 group을 리포트용 상위 group으로 묶습니다."""
    assert _summary_group("Positive") == "Positive"
    assert _summary_group("Authentication") == "Authentication"
    assert _summary_group("Validation - count") == "Validation - Query Params"
    assert _summary_group("Validation - skip") == "Validation - Query Params"
    assert _summary_group("Validation - filter_title") == "Validation - Query Params"
    assert _summary_group("Validation - headers") == "Validation - Headers"
    assert _summary_group("Validation - classroom_id") == "Validation - Path Params"
    assert _summary_group("Validation - title") == "Validation - Form Data"
    assert _summary_group("Validation - required fields") == "Validation - Form Data"
    assert _summary_group("Validation - context") == "Validation - Form Data"
    assert _summary_group("Validation - classroom_id", is_bug_candidate=True) == "Bug Candidates"


def test_record_result_ignores_tests_without_tc_metadata() -> None:
    """API summary에는 tc marker가 있는 API 케이스만 기록합니다."""
    report = SimpleNamespace(
        nodeid="tests/unit/test_api_reporting.py::test_unit",
        user_properties=[],
        passed=True,
        failed=False,
        skipped=False,
        outcome="passed",
        duration=0.01,
    )

    api_reporting._record_result(report)

    assert api_reporting.SUMMARY_RESULTS == []
    assert api_reporting.RECORDED_NODEIDS == set()


def test_record_result_uses_collected_tc_metadata_for_setup_skip_reports() -> None:
    """setup 단계에서 skip된 API 테스트도 collection metadata로 summary에 기록합니다."""
    nodeid = "tests/api/classroom_article/validation/test_case.py::test_case"
    api_reporting.TC_METADATA_BY_NODEID[nodeid] = {
        "tc_id": "API_AR_003",
        "group": "Validation - count",
        "summary_group": "Validation - Query Params",
        "title": "count 없음",
        "expected": "422",
    }
    report = SimpleNamespace(
        nodeid=nodeid,
        user_properties=[],
        passed=False,
        failed=False,
        skipped=True,
        outcome="skipped",
        duration=0.0,
        longrepr=("", "", "Skipped: Set RUN_LIVE_API_TESTS=1 to run live API tests."),
    )

    api_reporting._record_result(report)

    assert api_reporting.SUMMARY_RESULTS == [
        {
            "tc_id": "API_AR_003",
            "group": "Validation - count",
            "summary_group": "Validation - Query Params",
            "title": "count 없음",
            "expected": "422",
            "nodeid": nodeid,
            "status": "SKIPPED",
            "duration_seconds": 0.0,
            "detail": "Skipped: Set RUN_LIVE_API_TESTS=1 to run live API tests.",
        }
    ]
