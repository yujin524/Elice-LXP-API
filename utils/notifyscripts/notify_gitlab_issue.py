"""CI에서 FAILED로 판정된 TC를 GitLab 이슈로 자동 등록합니다.

reports/api-summary*.json(tests/api/plugins/api_reporting.py가 생성)에서 status=="FAILED"
항목을 모아, TC ID 기준으로 이미 열려있는 이슈가 있으면 재발 코멘트만 남기고(중복 이슈 방지),
없으면 팀 버그 리포트 템플릿 형식으로 새 이슈를 생성합니다.

GITLAB_API_TOKEN이 설정되지 않았거나 FAILED 케이스가 없으면 아무 것도 하지 않고 종료합니다.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
ALLURE_RESULTS_DIR = ROOT / "allure-results"
MAX_LOG_LINE_LEN = 200

GITLAB_API_URL = os.environ.get("GITLAB_API_URL", "https://kdt-gitlab.elice.io/api/v4").rstrip("/")
GITLAB_PROJECT_PATH = os.environ.get(
    "GITLAB_PROJECT_PATH", "qa_track/class_05/qa_project_02/team03/issue-report"
)
ISSUE_LABELS = "업무유형::버그,상태::TODO"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, "").strip() or default


def _load_failed_results() -> list[dict]:
    results: list[dict] = []
    for summary_file in sorted(REPORTS_DIR.glob("api-summary*.json")):
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        results.extend(summary.get("results", []))
    return [item for item in results if item.get("status") == "FAILED"]


def _domain_from_nodeid(nodeid: str) -> str:
    parts = nodeid.replace("\\", "/").split("/")
    if "api" in parts:
        idx = parts.index("api")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return "unknown"


def _truncate(text: str, limit: int = MAX_LOG_LINE_LEN) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _find_allure_log_text(tc_id: str) -> str | None:
    """Allure 결과에서 해당 TC의 로그 첨부 파일을 찾아 원문을 반환합니다."""
    if not ALLURE_RESULTS_DIR.exists():
        return None

    for result_file in ALLURE_RESULTS_DIR.glob("*-result.json"):
        try:
            data = json.loads(result_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        labels = {label.get("name"): label.get("value") for label in data.get("labels", [])}
        if labels.get("tc_id") != tc_id:
            continue

        for attachment in data.get("attachments", []):
            source = attachment.get("source")
            if not source:
                continue
            attachment_path = ALLURE_RESULTS_DIR / source
            if attachment_path.exists():
                return attachment_path.read_text(encoding="utf-8", errors="replace")

    return None


def _last_request_response(log_text: str) -> str | None:
    """로그 원문에서 실패 직전 마지막 요청/응답 한 줄씩만 뽑아 짧게 요약합니다.

    응답 body 전체를 그대로 넣으면 이슈가 한없이 길어지므로(예: 리스트 응답 통째로
    덤프), 요청/응답 요약 줄만 쓰고 body= 줄은 넣지 않습니다.
    """
    request_line = None
    response_line = None
    for line in log_text.splitlines():
        stripped = line.strip()
        if "→ 요청" in stripped:
            request_line = stripped.split("→", 1)[1].strip()
        elif "← 응답" in stripped:
            response_line = stripped.split("←", 1)[1].strip()

    if not request_line and not response_line:
        return None

    lines = []
    if request_line:
        lines.append(f"→ {_truncate(request_line)}")
    if response_line:
        lines.append(f"← {_truncate(response_line)}")
    return "\n".join(lines)


def _project_api_base(token: str) -> tuple[str, dict]:
    encoded_path = quote(GITLAB_PROJECT_PATH, safe="")
    base = f"{GITLAB_API_URL}/projects/{encoded_path}"
    headers = {"PRIVATE-TOKEN": token}
    return base, headers


def _issue_title(item: dict) -> str:
    return f"[Bug] [{item['tc_id']}] {item['title']}"


def _find_open_issue(base: str, headers: dict, tc_id: str) -> dict | None:
    response = requests.get(
        f"{base}/issues",
        headers=headers,
        params={"search": f"[{tc_id}]", "in": "title", "state": "opened"},
        timeout=15,
    )
    response.raise_for_status()
    for issue in response.json():
        if issue.get("title", "").startswith(f"[Bug] [{tc_id}]"):
            return issue
    return None


def _issue_description(item: dict, build_url: str, branch: str) -> str:
    domain = _domain_from_nodeid(item.get("nodeid", ""))
    log_text = _find_allure_log_text(item.get("tc_id", ""))
    request_response = _last_request_response(log_text) if log_text else None
    request_response_block = (
        f"```\n{request_response}\n```" if request_response else "(요청/응답 로그를 찾지 못함 — Allure 리포트 참고)"
    )
    return f"""📋 기본 정보

- 스페이스 : Issue Report (IR)
- 업무 유형 : 버그
- 상태 : TODO (CI 자동 등록)
- 우선순위 : (검토 필요)
- 컴포넌트 : {domain}

🔍 상세 내용

**Problem Description**
CI 자동화 테스트 `{item['tc_id']}` 실패

```
{item.get('detail', '(상세 메시지 없음)')}
```

**Expected Behavior**
{item.get('expected', '(TC 정의에 expected 없음)')}

**Reproduction Steps**
1. `{item['nodeid']}` pytest 케이스를 branch `{branch}`에서 실행

**Affected URL**
API 자동화 테스트 케이스라 화면 URL 없음 — 관련 pytest 노드: `{item['nodeid']}`

**Affected Account Email**
CI 전용 dev 테스트 계정 사용 (Jenkins credential 관리, 이슈 본문에 직접 노출 안 함)

📝 추가 설명

- Jenkins CI가 FAILED 판정 시 자동 생성. 재현 여부 확인 및 상세 내용 보완 필요
- 그룹: {item.get('group', '')}
- Jenkins 빌드: {build_url}

**요청/응답 (마지막 호출, 스크린샷 대체)**
{request_response_block}

/label ~"업무유형::버그" ~"상태::TODO"
"""


def _create_issue(base: str, headers: dict, item: dict, build_url: str, branch: str) -> None:
    payload = {
        "title": _issue_title(item),
        "description": _issue_description(item, build_url, branch),
        "labels": ISSUE_LABELS,
    }
    response = requests.post(f"{base}/issues", headers=headers, data=payload, timeout=15)
    response.raise_for_status()
    print(f"[GitLab Issue] 생성됨: {item['tc_id']} -> {response.json().get('web_url')}")


def _comment_on_issue(base: str, headers: dict, issue: dict, item: dict, build_url: str) -> None:
    body = (
        f"CI에서 재발 (다시 실패).\n\n"
        f"- 빌드: {build_url}\n"
        f"- 상세: {item.get('detail', '')}"
    )
    response = requests.post(
        f"{base}/issues/{issue['iid']}/notes",
        headers=headers,
        data={"body": body},
        timeout=15,
    )
    response.raise_for_status()
    print(f"[GitLab Issue] 기존 이슈에 재발 코멘트 추가: {item['tc_id']} -> {issue.get('web_url')}")


def register_failed_issues() -> None:
    token = os.environ.get("GITLAB_API_TOKEN")
    if not token:
        print("GITLAB_API_TOKEN이 설정되지 않아 GitLab 이슈 등록을 건너뜁니다.", file=sys.stderr)
        return

    failed_items = _load_failed_results() if REPORTS_DIR.exists() else []
    if not failed_items:
        print("FAILED 케이스가 없어 GitLab 이슈 등록을 건너뜁니다.")
        return

    build_url = _env("BUILD_URL", "")
    branch = _env("GIT_BRANCH_NAME", "develop")
    base, headers = _project_api_base(token)

    for item in failed_items:
        tc_id = item.get("tc_id", "")
        if not tc_id:
            continue
        existing = _find_open_issue(base, headers, tc_id)
        if existing:
            _comment_on_issue(base, headers, existing, item, build_url)
        else:
            _create_issue(base, headers, item, build_url, branch)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    register_failed_issues()


if __name__ == "__main__":
    main()
