"""API 테스트 결과 요약 pytest plugin.

이 파일은 conftest.py에서 분리한 "결과 정리" 전용 코드입니다.
conftest.py는 fixture와 실행 안전장치만 담당하고, 이 파일은 테스트 결과를 모아
콘솔/Markdown/JSON 리포트로 보여주는 일을 담당합니다.
"""

from __future__ import annotations
import json
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger


logger = get_logger()
SUMMARY_RESULTS: list[dict[str, object]] = []
RECORDED_NODEIDS: set[str] = set()
TC_METADATA_BY_NODEID: dict[str, dict[str, str]] = {}

SUMMARY_GROUP_MAP = {
    "Validation - count": "Validation - Query Params",
    "Validation - skip": "Validation - Query Params",
    "Validation - filter_title": "Validation - Query Params",
    "Validation - headers": "Validation - Headers",
    "Validation - classroom_id": "Validation - Path Params",
    "Validation - title": "Validation - Form Data",
    "Validation - required fields": "Validation - Form Data",
    "Validation - context": "Validation - Form Data",
}


def _summary_group(group: str, *, is_bug_candidate: bool = False) -> str:
    """테스트 케이스의 세부 group을 리포트 요약용 상위 group으로 변환합니다."""
    if is_bug_candidate:
        return "Bug Candidates"

    return SUMMARY_GROUP_MAP.get(group, group)


def apply_tc_metadata(item) -> None:
    """pytest item에 붙은 tc marker 정보를 결과 요약용 속성으로 복사합니다.

    테스트 코드의 `@pytest.mark.tc(...)` 값은 기본 pytest 결과에는 바로 나오지 않습니다.
    그래서 수집 단계에서 `user_properties`로 옮겨 두고, 테스트 종료 후 요약 리포트에 사용합니다.
    """
    marker = item.get_closest_marker("tc")
    if not marker:
        return

    existing_keys = {key for key, _ in item.user_properties}
    group = marker.kwargs.get("group", "")
    metadata = {
        "tc_id": marker.kwargs.get("id", ""),
        "group": group,
        "summary_group": _summary_group(
            group,
            is_bug_candidate=item.get_closest_marker("bug_candidate") is not None,
        ),
        "title": marker.kwargs.get("title", ""),
        "expected": marker.kwargs.get("expected", ""),
    }
    TC_METADATA_BY_NODEID[item.nodeid] = metadata

    for key, value in metadata.items():
        if key not in existing_keys:
            item.user_properties.append((key, value))


def _report_status(report) -> str:
    if hasattr(report, "wasxfail") and report.skipped:
        return "XFAILED"
    if hasattr(report, "wasxfail") and report.passed:
        return "XPASSED"
    if report.passed:
        return "PASSED"
    if report.failed:
        return "FAILED"
    if report.skipped:
        return "SKIPPED"
    return report.outcome.upper()


def _short_detail(report) -> str:
    if hasattr(report, "wasxfail"):
        return str(report.wasxfail)
    if report.skipped:
        if isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
            return str(report.longrepr[2])
        return str(report.longrepr)
    if report.failed:
        return str(report.longrepr).splitlines()[-1][:300]
    return ""


def _record_result(report) -> None:
    if report.nodeid in RECORDED_NODEIDS:
        return

    props = {
        **TC_METADATA_BY_NODEID.get(report.nodeid, {}),
        **dict(report.user_properties),
    }
    if not props.get("tc_id"):
        return

    status = _report_status(report)
    SUMMARY_RESULTS.append(
        {
            "tc_id": props.get("tc_id", ""),
            "group": props.get("group", "Unclassified"),
            "summary_group": props.get("summary_group", props.get("group", "Unclassified")),
            "title": props.get("title", report.nodeid),
            "expected": props.get("expected", ""),
            "nodeid": report.nodeid,
            "status": status,
            "duration_seconds": round(report.duration, 3),
            "detail": _short_detail(report),
        }
    )
    RECORDED_NODEIDS.add(report.nodeid)


def _display_width(text: str) -> int:
    """터미널에서 한글 등 동아시아 문자가 2칸을 차지하는 걸 반영한 표시 폭을 계산함."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad_display(text: str, width: int) -> str:
    return text + " " * max(width - _display_width(text), 0)


def _status_badge(status: str) -> str:
    return {
        "PASSED": "PASS",
        "FAILED": "FAIL",
        "SKIPPED": "SKIP",
        "XFAILED": "XFAIL",
        "XPASSED": "XPASS",
    }.get(status, status)


def _write_summary_reports(config) -> None:
    if not SUMMARY_RESULTS:
        return

    reports_dir = Path(config.rootpath) / "reports"
    reports_dir.mkdir(exist_ok=True)

    ordered = sorted(SUMMARY_RESULTS, key=lambda item: item["tc_id"] or item["nodeid"])
    counts = Counter(item["status"] for item in ordered)
    groups = defaultdict(Counter)
    for item in ordered:
        summary_group = item.get("summary_group", item["group"])
        groups[summary_group][item["status"]] += 1
        groups[summary_group]["TOTAL"] += 1

    summary_json = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(ordered),
        "counts": dict(counts),
        "groups": {group: dict(counter) for group, counter in groups.items()},
        "results": ordered,
    }
    (reports_dir / "api-summary.json").write_text(
        json.dumps(summary_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if counts.get("FAILED", 0):
        verdict = "FAIL - 실패 케이스 확인 필요"
    elif counts.get("XPASSED", 0):
        verdict = "CHECK - 예상 실패 케이스가 통과함"
    elif len(ordered) > 0 and counts.get("SKIPPED", 0) == len(ordered):
        verdict = "SKIP - 라이브 API 실행 조건 미설정"
    else:
        verdict = "PASS - 주요 실패 없음"

    group_order = [
        "Positive",
        "Validation - Query Params",
        "Validation - Headers",
        "Authentication",
        "Validation - Path Params",
        "Bug Candidates",
    ]
    ordered_groups = [group for group in group_order if group in groups]
    ordered_groups.extend(sorted(group for group in groups if group not in group_order))

    lines = [
        "# API Test Summary",
        "",
        "## 한눈에 보기",
        "",
        f"- 실행 판정: {verdict}",
        f"- Generated At: {summary_json['generated_at']}",
        f"- 전체: {summary_json['total']}",
        f"- 통과: {counts.get('PASSED', 0)}",
        f"- 실패: {counts.get('FAILED', 0)}",
        f"- 스킵: {counts.get('SKIPPED', 0)}",
        f"- 예상 실패: {counts.get('XFAILED', 0)}",
        f"- 예상과 다르게 통과: {counts.get('XPASSED', 0)}",
        "",
        "## 결과 해석",
        "",
    ]
    if len(ordered) > 0 and counts.get("SKIPPED", 0) == len(ordered):
        lines.extend(
            [
                "모든 테스트가 SKIP이면 실제 API 호출이 실행되지 않은 상태입니다.",
                "`RUN_LIVE_API_TESTS=1`을 설정한 뒤 다시 실행하세요.",
            ]
        )
    elif counts.get("FAILED", 0):
        lines.append("FAILED 케이스가 있으면 아래 `확인 필요 케이스` 표를 먼저 확인하세요.")
    elif counts.get("XPASSED", 0):
        lines.append("XPASS는 버그 후보로 표시한 케이스가 예상과 다르게 통과했다는 뜻입니다.")
    else:
        lines.append("실패 또는 예상과 다른 통과 케이스가 없습니다.")

    lines.extend(
        [
            "",
            "## 그룹별 요약",
            "",
            "| Group | Total | Pass | Fail | Skip | XFail | XPass |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for group in ordered_groups:
        counter = groups[group]
        lines.append(
            "| {group} | {total} | {passed} | {failed} | {skipped} | {xfailed} | {xpassed} |".format(
                group=group,
                total=counter.get("TOTAL", 0),
                passed=counter.get("PASSED", 0),
                failed=counter.get("FAILED", 0),
                skipped=counter.get("SKIPPED", 0),
                xfailed=counter.get("XFAILED", 0),
                xpassed=counter.get("XPASSED", 0),
            )
        )

    attention = [item for item in ordered if item["status"] in {"FAILED", "XPASSED"}]
    lines.extend(["", "## 확인 필요 케이스", ""])
    if attention:
        lines.extend(["| TC ID | Result | Group | Case | Expected | Detail |", "|---|---|---|---|---|---|"])
        for item in attention:
            lines.append(
                f"| {item['tc_id']} | {_status_badge(item['status'])} | {item['group']} | "
                f"{item['title']} | {item['expected']} | {item['detail']} |"
            )
    else:
        lines.append("실패하거나 예상과 다르게 통과한 케이스가 없습니다.")

    lines.extend(
        [
            "",
            "## 전체 케이스",
            "",
            "| TC ID | Result | Group | Case | Expected | Duration(s) |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for item in ordered:
        lines.append(
            f"| {item['tc_id']} | {_status_badge(item['status'])} | {item['group']} | "
            f"{item['title']} | {item['expected']} | {item['duration_seconds']} |"
        )

    (reports_dir / "api-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")



def print_group_summary(write_line, ordered: list[dict]) -> None:
    """그룹별 Total/Pass/Fail/Skip/XFail/XPass 집계 표를 write_line으로 출력함.
    api-summary.md의 '그룹별 요약' 표와 같은 집계 로직을 콘솔용으로 재계산함.
    write_line은 terminalreporter.write_line처럼 (text, **markup)을 받는 호출 가능 객체면 됨
    (pytest 실행 중엔 terminalreporter.write_line, 병합 요약 스크립트에선 print 래퍼를 넘김)."""
    groups: dict[str, Counter] = defaultdict(Counter)
    for item in ordered:
        summary_group = item.get("summary_group", item["group"])
        groups[summary_group][item["status"]] += 1
        groups[summary_group]["TOTAL"] += 1

    group_order = [
        "Positive",
        "Validation - Query Params",
        "Validation - Headers",
        "Authentication",
        "Validation - Path Params",
        "Bug Candidates",
    ]
    ordered_groups = [group for group in group_order if group in groups]
    ordered_groups.extend(sorted(group for group in groups if group not in group_order))

    name_width = max([len("Group")] + [len(group) for group in ordered_groups])

    def _row(name: str, counter: Counter) -> str:
        return (
            f"  {_pad_display(name, name_width)} {counter.get('TOTAL', 0):>5} {counter.get('PASSED', 0):>5} "
            f"{counter.get('FAILED', 0):>5} {counter.get('SKIPPED', 0):>5} "
            f"{counter.get('XFAILED', 0):>5} {counter.get('XPASSED', 0):>5}"
        )

    write_line("")
    write_line("📋 그룹별 요약", bold=True)
    write_line(f"  {'Group':<{name_width}} {'Total':>5} {'Pass':>5} {'Fail':>5} {'Skip':>5} {'XFail':>5} {'XPass':>5}")
    total_counter: Counter = Counter()
    for group in ordered_groups:
        counter = groups[group]
        write_line(_row(group, counter))
        total_counter.update(counter)

    write_line(f"  {'-' * name_width} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5}")
    write_line(_row("합계", total_counter))


def print_detail_section(write_line, items: list[dict], heading: str, *, show_detail: bool, **markup) -> None:
    """FAIL/SKIP 항목을 tc_id·제목과 함께 write_line으로 출력함.
    show_detail=True면 실제 사유(assert 메시지/skip 사유)까지 한 줄 더 붙임."""
    if not items:
        return

    write_line("")
    write_line(heading, **markup)
    for item in items:
        write_line(f"  [{item['tc_id']}] {item['title']}")
        if show_detail and item.get("detail"):
            write_line(f"    └ {item['detail']}")


def pytest_collection_modifyitems(config, items) -> None:
    """수집된 테스트의 tc marker 정보를 summary용 metadata로 저장합니다."""
    for item in items:
        apply_tc_metadata(item)
def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    """스테이지별 콘솔 요약은 찍지 않고, JSON/Markdown 리포트만 생성합니다.
    prod/dev 스테이지를 합친 통합 요약은 utils/notifyscripts/notify_discord.py가 콘솔에 한 번만 출력합니다."""
    if not SUMMARY_RESULTS:
        return

    _write_summary_reports(config)


def pytest_report_teststatus(report, config):
    """pytest 기본 진행 문자 대신 최종 요약만 보이게 합니다."""
    is_final_result = report.when == "call"
    is_setup_stop = report.when == "setup" and (report.skipped or report.failed)
    if not (is_final_result or is_setup_stop):
        return None

    status = _report_status(report)
    category = {
        "PASSED": "passed",
        "FAILED": "failed",
        "SKIPPED": "skipped",
        "XFAILED": "xfailed",
        "XPASSED": "xpassed",
    }.get(status, report.outcome)

    return category, "", ""


def pytest_runtest_logreport(report) -> None:
    """각 테스트 케이스의 PASS/FAIL/SKIP 결과를 로그와 summary 데이터에 남깁니다."""
    if report.when == "setup" and report.skipped:
        logger.info("[SKIP] %s", report.nodeid)
        _record_result(report)
        return

    if report.when == "setup" and report.failed:
        logger.error("[FAIL] %s", report.nodeid)
        _record_result(report)
        return

    if report.when != "call":
        return

    if report.passed:
        logger.info("[PASS] %s", report.nodeid)
    elif report.failed:
        logger.error("[FAIL] %s", report.nodeid)
    elif report.skipped:
        logger.info("[SKIP] %s", report.nodeid)
    _record_result(report)

