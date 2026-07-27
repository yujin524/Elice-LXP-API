"""Jenkins 빌드 결과를 Discord webhook으로 요약해서 보냅니다.

reports/api-summary*.json(tests/api/plugins/api_reporting.py가 생성)을 읽어서
성공/실패/스킵 집계와 실패 목록을 만들고, Jenkins 빌드/Allure 리포트 링크와 함께
Discord webhook으로 전송합니다.

prod/dev처럼 서로 다른 환경변수로 pytest를 여러 번 돌리는 파이프라인에서는
매 실행마다 api-summary.json이 통째로 새로 쓰여지므로(Run 별 별도 프로세스),
Jenkinsfile이 이전 실행 결과를 api-summary-<name>.json으로 옮겨두고, 여기서는
reports/ 아래의 api-summary*.json을 전부 읽어 합쳐서 하나의 결과로 보여준다.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"

sys.path.insert(0, str(ROOT))
from tests.api.plugins.api_reporting import (  # noqa: E402
    print_detail_section,
    print_group_summary,
)

MAX_FAILURES_SHOWN = 3


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, "").strip() or default


def _load_all_results() -> list[dict]:
    results: list[dict] = []
    for summary_file in sorted(REPORTS_DIR.glob("api-summary*.json")):
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        results.extend(summary.get("results", []))
    return results


def _attention_list_lines(items: list[dict], heading: str) -> list[str]:
    if not items:
        return []

    ordered = sorted(items, key=lambda item: item.get("tc_id") or item.get("nodeid", ""))
    lines = ["", heading]
    for item in ordered[:MAX_FAILURES_SHOWN]:
        title = item.get("title") or item.get("nodeid", "")
        lines.append(f"  · [{item.get('tc_id', '')}] {title}")
    remaining = len(ordered) - MAX_FAILURES_SHOWN
    if remaining > 0:
        lines.append(f"  외 {remaining}건")
    return lines


def build_message() -> str:
    team = _env("DISCORD_TEAM_NAME", "team-3")
    project = _env("DISCORD_PROJECT_NAME", "200_project")
    branch = _env("GIT_BRANCH_NAME", "develop")
    author = _env("GIT_AUTHOR_NAME", "unknown")
    commit_message = _env("GIT_COMMIT_MESSAGE", "")
    build_url = _env("BUILD_URL", "")
    allure_url = _env("ALLURE_REPORT_URL", "")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    results = _load_all_results() if REPORTS_DIR.exists() else []

    if not results:
        lines = [
            f"⚠️ {team} : {project} — {branch} 테스트 완료",
            f"📅 {now}  |  👤 {author}",
            f"💬 {commit_message}",
            "",
            "테스트 결과 리포트를 찾지 못했습니다. (reports/api-summary*.json 없음)",
        ]
    else:
        counts: dict[str, int] = {}
        for item in results:
            status = item.get("status", "")
            counts[status] = counts.get(status, 0) + 1

        passed = counts.get("PASSED", 0)
        skipped = counts.get("SKIPPED", 0)
        xfailed = counts.get("XFAILED", 0)
        failed_items = [item for item in results if item.get("status") == "FAILED"]
        xpassed_items = [item for item in results if item.get("status") == "XPASSED"]
        failed = len(failed_items)
        xpassed = len(xpassed_items)
        total = len(results)

        header_emoji = "❌" if failed else ("⚠️" if xpassed else "✅")

        lines = [
            f"{header_emoji} {team} : {project} — {branch} 테스트 완료",
            f"📅 {now}  |  👤 {author}",
            f"💬 {commit_message}",
            "",
            f"✅ 성공: {passed}  ❌ 실패: {failed}  ⏭ 스킵: {skipped}  ⚠️ XPASS: {xpassed}  🟡 XFAIL: {xfailed}  합계: {total}",
        ]

        lines.extend(_attention_list_lines(failed_items, "❌ 실패 목록:"))
        lines.extend(_attention_list_lines(xpassed_items, "⚠️ XPASSED 목록:"))

    lines.append("")
    if allure_url:
        lines.append(f"📊 Allure 리포트: {allure_url}")
    if build_url:
        lines.append(f"🔗 파이프라인: {build_url}")

    return "\n".join(lines)


def _console_write_line(text: str = "", **_markup) -> None:
    print(text)


def print_console_summary(results: list[dict]) -> None:
    """prod/dev 스테이지를 합친 전체 결과를 Jenkins 콘솔에 출력함.
    각 pytest 스테이지의 콘솔 로그는 그 스테이지 결과만 보여주므로,
    Discord로 보내는 합산 수치(성공/실패/스킵/XFAIL)와 콘솔 로그를 맞추기 위해
    api_reporting.py의 표 출력 로직을 재사용해 여기서 한 번 더 통합 요약을 찍는다."""
    if not results:
        return

    ordered = sorted(results, key=lambda item: item.get("tc_id") or item.get("nodeid", ""))

    print("")
    print("===== 통합 결과 요약 (prod + dev) =====")
    print_group_summary(_console_write_line, ordered)

    failed_items = [item for item in ordered if item.get("status") == "FAILED"]
    xpassed_items = [item for item in ordered if item.get("status") == "XPASSED"]
    xfailed_items = [item for item in ordered if item.get("status") == "XFAILED"]
    skipped_items = [item for item in ordered if item.get("status") == "SKIPPED"]
    print_detail_section(_console_write_line, failed_items, "❌ FAILED 상세", show_detail=True)
    print_detail_section(_console_write_line, xpassed_items, "⚠️ XPASSED 상세", show_detail=True)
    print_detail_section(_console_write_line, xfailed_items, "🟡 XFAILED 목록", show_detail=False)
    print_detail_section(_console_write_line, skipped_items, "⏭ SKIPPED 목록", show_detail=False)


def send_to_discord(message: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL이 설정되지 않아 Discord 전송을 건너뜁니다.", file=sys.stderr)
        return

    response = requests.post(webhook_url, json={"content": message}, timeout=10)
    response.raise_for_status()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if REPORTS_DIR.exists():
        print_console_summary(_load_all_results())

    message = build_message()
    send_to_discord(message)


if __name__ == "__main__":
    main()
