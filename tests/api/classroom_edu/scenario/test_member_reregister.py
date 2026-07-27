# 구성원 제거 후 재등록 시나리오 테스트 — API_CH_034

from __future__ import annotations
import logging
import time
import pytest
from tests.api.common.assertions import assert_member_list, assert_member_mutation_success

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.api

API_CH_034_TC = dict(id="API_CH_034", group="Scenario", title="구성원 제거 후 재등록", expected="제거 확인 후 재등록으로 원복")


def _find_member_by_account_id(members: list[dict], account_id: int) -> dict | None:
    return next((m for m in members if m.get("account_id") == account_id), None)


def _poll_member_by_account_id(member_page, *, classroom_id: str, account_id: int, timeout: int = 20, interval: int = 2):
    deadline = time.time() + timeout
    while time.time() < deadline:
        members = assert_member_list(
            member_page.get_member_list(classroom_id=classroom_id, filter_roles="student", count=50)
        )
        match = _find_member_by_account_id(members, account_id)
        if match is not None:
            return match
        time.sleep(interval)
    return None


@pytest.mark.tc(**API_CH_034_TC)
def test_member_remove_and_reregister(member_page, classroom_id: str, learner_account_id: int) -> None:
    """학습자 계정을 클래스에서 제거했다가 다시 등록해 원래 상태로 복원한다.

    기존 데이터 훼손 방지를 위해 제거→재등록 순서로 진행한다. 재등록(POST /member/bulk)은
    비동기(task_id만 반환)라, 재등록 반영 여부는 구성원 목록을 폴링해서 확인한다."""
    logger.info("▶ [API_CH_034] 현재 구성원에서 학습자(account_id=%s) 찾는 중", learner_account_id)
    members = assert_member_list(
        member_page.get_member_list(classroom_id=classroom_id, filter_roles="student", count=50)
    )
    existing = _find_member_by_account_id(members, learner_account_id)
    if existing is None:
        pytest.skip(f"현재 구성원 목록에서 학습자(account_id={learner_account_id})를 찾지 못했습니다.")
    member_id = existing["id"]

    logger.info("  └ Step1: 구성원 제거 (member_id=%s)", member_id)
    remove_resp = member_page.remove_member(member_id=member_id, classroom_id=classroom_id)
    assert_member_mutation_success(remove_resp, "API_CH_034 | remove member")

    try:
        logger.info("  └ Step2: 구성원 재등록 (account_id=%s)", learner_account_id)
        add_resp = member_page.add_members_bulk(
            classroom_id=classroom_id, account_ids=[learner_account_id], role="student"
        )
        assert_member_mutation_success(add_resp, "API_CH_034 | re-add member")

        logger.info("  └ Step3: 목록 조회하여 재등록 반영 확인 (폴링)")
        restored = _poll_member_by_account_id(member_page, classroom_id=classroom_id, account_id=learner_account_id)
        assert restored is not None, "재등록이 시간 내에 목록에 반영되지 않았습니다. (비동기 처리 지연 가능)"
        logger.info("  └ 재등록 확인 완료: 새 member_id=%s", restored["id"])
    except Exception:
        logger.error(
            "  └ 재등록 실패 — account_id=%s가 클래스에서 제거된 상태로 남아있을 수 있습니다. 수동 확인 필요.",
            learner_account_id,
        )
        raise
