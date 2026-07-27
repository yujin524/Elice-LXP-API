"""Jenkins API 테스트 결과를 Slack Incoming Webhook으로 전송합니다.

기존 Discord 알림 코드를 수정하지 않기 위해 이 파일에서 결과 파일 읽기,
상태 집계, 메시지 작성, Slack 전송을 독립적으로 처리합니다.

Webhook URL은 코드에 저장하지 않고 Jenkins Credentials를 통해
``SLACK_WEBHOOK_URL`` 환경변수로 전달받습니다.
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
MAX_FAILURES_SHOWN = 3


def _env(name: str, default: str = "") -> str:
    """공백인 환경변수에는 기본값을 적용합니다."""

    return os.environ.get(name, "").strip() or default


def _load_all_results() -> list[dict]:
    """prod/dev 실행이 남긴 모든 API 요약 파일의 TC 결과를 합칩니다."""

    results: list[dict] = []
    for summary_file in sorted(REPORTS_DIR.glob("api-summary*.json")):
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        results.extend(summary.get("results", []))
    return results


def build_message() -> str:
    """Slack에 표시할 빌드 정보와 테스트 결과 요약을 만듭니다."""

    team = _env("SLACK_TEAM_NAME", "team-3")
    project = _env("SLACK_PROJECT_NAME", "200_project")
    branch = _env("GIT_BRANCH_NAME", "develop")
    author = _env("GIT_AUTHOR_NAME", "unknown")
    commit_message = _env("GIT_COMMIT_MESSAGE", "")
    build_url = _env("BUILD_URL", "")
    allure_url = _env("ALLURE_REPORT_URL", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    results = _load_all_results() if REPORTS_DIR.exists() else []

    if not results:
        lines = [
            f"⚠️ *{team} : {project} — {branch} 테스트 완료*",
            f"📅 {now}  |  👤 {author}",
            f"💬 {commit_message}",
            "",
            "테스트 결과 리포트를 찾지 못했습니다. "
            "(`reports/api-summary*.json` 없음)",
        ]
    else:
        counts: dict[str, int] = {}
        for item in results:
            status = item.get("status", "")
            counts[status] = counts.get(status, 0) + 1

        passed = counts.get("PASSED", 0)
        skipped = counts.get("SKIPPED", 0)
        xfailed = counts.get("XFAILED", 0)
        attention = [
            item for item in results if item.get("status") in {"FAILED", "XPASSED"}
        ]
        failed = len(attention)
        total = len(results)
        header_emoji = "❌" if failed else "✅"

        lines = [
            f"{header_emoji} *{team} : {project} — {branch} 테스트 완료*",
            f"📅 {now}  |  👤 {author}",
            f"💬 {commit_message}",
            "",
            (
                f"✅ 성공: *{passed}*  ❌ 실패: *{failed}*  "
                f"⏭ 스킵: *{skipped}*  🟡 XFAIL: *{xfailed}*  "
                f"합계: *{total}*"
            ),
        ]

        if attention:
            ordered_attention = sorted(
                attention,
                key=lambda item: item.get("tc_id") or item.get("nodeid", ""),
            )
            lines.extend(["", "❌ *실패 목록*"])
            for item in ordered_attention[:MAX_FAILURES_SHOWN]:
                title = item.get("title") or item.get("nodeid", "")
                lines.append(f"• `[{item.get('tc_id', '')}]` {title}")

            remaining = len(ordered_attention) - MAX_FAILURES_SHOWN
            if remaining > 0:
                lines.append(f"• 외 {remaining}건")

    lines.append("")
    if allure_url:
        lines.append(f"📊 <{allure_url}|Allure 리포트>")
    if build_url:
        lines.append(f"🔗 <{build_url}|Jenkins 파이프라인>")

    return "\n".join(lines)


def send_to_slack(message: str) -> None:
    """Slack Incoming Webhook에 메시지를 전송합니다."""

    webhook_url = _env("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print(
            "SLACK_WEBHOOK_URL이 설정되지 않아 Slack 전송을 건너뜁니다.",
            file=sys.stderr,
        )
        return

    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()


def main() -> None:
    """UTF-8 콘솔을 설정하고 Slack 알림을 전송합니다."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    send_to_slack(build_message())


if __name__ == "__main__":
    main()
