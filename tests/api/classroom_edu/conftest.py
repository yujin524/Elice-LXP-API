"""classroom_edu(교육자 클래스 홈 대시보드) API 테스트 전용 fixture 모음.

인증/클라이언트, classroom_id 등 공용 fixture는 루트 conftest.py를 그대로 쓰고,
여기서는 이 도메인 전용 page 객체와 권한 경계 테스트용 학습자(learner) 계정을 관리합니다.
course_edu와 마찬가지로 dev 서버에서 실행하지만, 기본 api_client는 루트 fixture를 사용하고
학습자 권한 검증에 필요한 LEARNER_ID/LEARNER_PW만 별도로 읽습니다.
"""

from __future__ import annotations
import base64
import json
import logging
import os
import pytest
from apis.classroom_edu.dashboard import ClassroomDashboardPage
from apis.classroom_edu.member import MemberPage
from config import settings
from utils.api_client import ApiClient
from utils.auth_token import get_token

logger = logging.getLogger(__name__)

LEARNER_ID = os.getenv("LEARNER_ID", "").strip()
LEARNER_PW = os.getenv("LEARNER_PW", "")


@pytest.fixture
def classroom_dashboard_page(api_client) -> ClassroomDashboardPage:
    """정상 Authorization 헤더와 org 헤더가 포함된 ClassroomDashboardPage."""
    return ClassroomDashboardPage(api_client)


@pytest.fixture
def member_page(api_client) -> MemberPage:
    """정상 Authorization 헤더와 org 헤더가 포함된 MemberPage."""
    return MemberPage(api_client)


@pytest.fixture(scope="session")
def learner_access_token() -> str:
    """학습자 계정으로 로그인해 access_token을 발급받는다. (권한 경계 테스트 전용)"""
    try:
        token = get_token(LEARNER_ID, LEARNER_PW)
    except RuntimeError as exc:
        pytest.skip(f"학습자 계정 로그인 실패({LEARNER_ID}): {exc}")
    logger.info("[준비] 학습자(learner) 토큰 발급 완료: %s", LEARNER_ID)
    return token


@pytest.fixture(scope="session")
def learner_api_client(requests_session, learner_access_token: str) -> ApiClient:
    """학습자 토큰 + org 헤더가 붙은 client."""
    return ApiClient(requests_session, settings, access_token=learner_access_token)


@pytest.fixture(scope="session")
def learner_account_id(learner_access_token: str) -> int:
    """학습자 access_token(JWT)에서 account id(_id)를 추출한다. (CH_034 구성원 제거/재등록 대상 식별용)"""
    try:
        payload_b64 = learner_access_token.split(".")[1]
        padded_payload = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload))
    except (IndexError, ValueError, json.JSONDecodeError):
        pytest.skip("학습자 토큰에서 account id를 추출하지 못했습니다.")

    account_id = payload.get("_id")
    if account_id is None:
        pytest.skip("학습자 토큰에 _id가 없습니다.")

    logger.info("[준비] learner_account_id 확보(JWT): %s", account_id)
    return account_id


# CH_032 self-scope 검증에서 실제로 학습자 1명만 등록된 상태를 확인한 classroom_id.
# 공용 classroom_id를 매번 동적으로 조회하면, 다른 자동화(부하테스트 등)가 같은 classroom의
# 멤버를 바꿔치기해서 실행 시점마다 학습자 등록 여부가 달라져 self-scope 검증이
# 비결정적으로 실패했다. 검증 완료된 classroom_id를 고정값으로 써서 이 문제를 없앤다.
CH032_CLASSROOM_ID = "22e01595-3c49-4605-8239-fe3473cd7e07"


@pytest.fixture(scope="session")
def ch032_classroom_id() -> str:
    """CH_032 self-scope 검증 전용 classroom_id (고정값)."""
    return CH032_CLASSROOM_ID
