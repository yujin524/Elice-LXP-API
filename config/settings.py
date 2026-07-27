"""API 테스트에서 사용하는 설정값 모음.

Postman의 Environment에 적어둔 값을 Python 파일로 옮긴 것이라고 보면 됩니다.
API 주소, classroom_id, org 같은 공통 설정을 여기서 관리합니다.

주의:
- access_token, login_id, password 같은 민감정보는 이 파일에 저장하지 않습니다.
- access_token은 pytest 실행 중 발급받아 fixture가 메모리에서 공유합니다.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 프로젝트 루트의 .env 파일을 읽습니다.
# 다른 폴더에서 pytest를 실행해도 config/settings.py 위치를 기준으로
# 프로젝트 루트의 .env를 찾습니다.
ENV_FILE = os.getenv("ENV_FILE", ".env")
load_dotenv(PROJECT_ROOT / ENV_FILE)


def _get_float_env(name: str, default: str) -> float:
    """환경변수 값을 숫자로 읽습니다. timeout 설정에 사용합니다."""
    value = os.getenv(name, default)
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number. current value: {value}") from exc


def _get_required_env(name: str) -> str:
    """필수 환경변수 값을 읽습니다. 비어 있으면 설정 누락을 바로 알립니다."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required. Check {ENV_FILE}.")
    return value


def _get_bool_env(name: str, default: str = "false") -> bool:
    """환경변수 값을 boolean으로 읽습니다."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_test_env() -> str:
    """지원하는 실행 환경(dev/prod)만 허용합니다."""
    value = os.getenv("TEST_ENV", "prod").strip().lower()
    if value not in {"dev", "prod"}:
        raise RuntimeError(f"TEST_ENV must be dev or prod. current value: {value}")
    return value


# --- 도메인 설정 ---
TEST_ENV = _get_test_env()
API_BASE_URL = _get_required_env("API_BASE_URL").rstrip("/")
REST_BASE_URL = _get_required_env("REST_BASE_URL").rstrip("/")
COURSE_BASE_URL = _get_required_env("COURSE_BASE_URL").rstrip("/")
DASHBOARD_BASE_URL = _get_required_env("DASHBOARD_BASE_URL").rstrip("/")
AUTH_URL = _get_required_env("AUTH_URL").rstrip("/")

# course_edu(교육자) 전용 REST host. course/schedule 등이 공유하는 REST_BASE_URL이 운영으로
# 바뀌어도 course_edu는 항상 dev 서버를 쓰도록 별도 이름으로 분리한다. course와 달리 dev 서버가
# 항상 고정이라 필수값이 아니라 기본값이 있는 선택 항목으로 둔다.
EDU_REST_BASE_URL = os.getenv("EDU_REST_BASE_URL", "https://dev-qatrack-api.dev.elicer.io").rstrip("/")

# --- 계정 받아오기 ---
ELICE_ID = os.getenv("ELICE_ID", "")
ELICE_PW = os.getenv("ELICE_PW", "")

# --- 권한 경계 테스트 계정 (선택) ---
# 선택된 env 파일에 역할별 계정이 모두 있을 때만 해당 권한 테스트를 실행합니다.
# 운영/Dev 환경명으로 분기하지 않으므로, 나중에 운영 계정을 추가해도 코드 변경이 필요 없습니다.
DEV_EDUCATOR_A_ID = os.getenv("DEV_EDUCATOR_A_ID", "").strip()
DEV_EDUCATOR_A_PW = os.getenv("DEV_EDUCATOR_A_PW", "")
DEV_EDUCATOR_B_ID = os.getenv("DEV_EDUCATOR_B_ID", "").strip()
DEV_EDUCATOR_B_PW = os.getenv("DEV_EDUCATOR_B_PW", "")
DEV_LEARNER_A_ID = os.getenv("DEV_LEARNER_A_ID", "").strip()
DEV_LEARNER_A_PW = os.getenv("DEV_LEARNER_A_PW", "")
DEV_LEARNER_B_ID = os.getenv("DEV_LEARNER_B_ID", "").strip()
DEV_LEARNER_B_PW = os.getenv("DEV_LEARNER_B_PW", "")
DEV_OUTSIDER_ID = os.getenv("DEV_OUTSIDER_ID", "").strip()
DEV_OUTSIDER_PW = os.getenv("DEV_OUTSIDER_PW", "")
AUTHZ_CLASSROOM_ID = os.getenv("AUTHZ_CLASSROOM_ID", "").strip()
ALLOW_PROD_AUTHZ_MUTATION_TESTS = _get_bool_env("ALLOW_PROD_AUTHZ_MUTATION_TESTS")

# --- 공통 식별자 ---
ELICE_ORG_NAME_SHORT = os.getenv("ELICE_ORG_NAME_SHORT", "qatrack")

# --- classroom 조회 정책 ---
CLASSROOM_LOOKUP_MODE = os.getenv("CLASSROOM_LOOKUP_MODE", "name_keyword").strip().lower()
CLASSROOM_NAME_KEYWORD = os.getenv("CLASSROOM_NAME_KEYWORD", "QA 트랙")
CLASSROOM_REQUIRE_OPENED = _get_bool_env("CLASSROOM_REQUIRE_OPENED")
CLASSROOM_REQUIRE_COURSE = _get_bool_env("CLASSROOM_REQUIRE_COURSE")

# --- 요청 설정 ---
API_TIMEOUT_SECONDS = _get_float_env("API_TIMEOUT_SECONDS", "10")
