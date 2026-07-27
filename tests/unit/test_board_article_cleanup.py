# 게시글 자동화 정리(cleanup) 유틸리티 단위 테스트 — API_BAE_B_001, API_BAD_B_001

from __future__ import annotations
import re
from types import SimpleNamespace
import pytest
from tests.api.board.article_cleanup import (
    BOARD_AUTOMATION_TITLE_PREFIX,
    BoardArticleCleanupError,
    BoardArticleCleanupRegistry,
    build_automation_article_title,
)


class FakeBoardApi:
    calls: list[tuple[object, dict]] = []

    def __init__(self, client) -> None:
        self.client = client

    def post_delete_article(self, *, data):
        self.calls.append((self.client, data))
        return SimpleNamespace(ok=True)


@pytest.fixture(autouse=True)
def clear_fake_calls():
    FakeBoardApi.calls.clear()


def test_automation_title_contains_prefix_tc_id_and_unique_suffix() -> None:
    title = build_automation_article_title("API_BAE_B_001")

    assert title.startswith(f"{BOARD_AUTOMATION_TITLE_PREFIX}[API_BAE_B_001]")
    assert re.fullmatch(
        r"\[QA-AUTO\]\[AUTHZ\]\[API_BAE_B_001\]\[[0-9a-f]{8}\]",
        title,
    )


def test_cleanup_uses_each_articles_owner_client() -> None:
    owner_a = object()
    owner_b = object()
    registry = BoardArticleCleanupRegistry(
        api_factory=FakeBoardApi,
        delete_assertion=lambda response: None,
    )
    registry.track(101, owner_a, tc_id="TC_A", owner_role="learner_a")
    registry.track(202, owner_b, tc_id="TC_B", owner_role="educator_a")

    registry.cleanup()

    assert FakeBoardApi.calls == [
        (owner_a, {"board_article_id": 101}),
        (owner_b, {"board_article_id": 202}),
    ]


def test_mark_deleted_prevents_duplicate_cleanup_request() -> None:
    registry = BoardArticleCleanupRegistry(
        api_factory=FakeBoardApi,
        delete_assertion=lambda response: None,
    )
    registry.track(101, object(), tc_id="TC_A")
    registry.mark_deleted(101)

    registry.cleanup()

    assert FakeBoardApi.calls == []


def test_cleanup_error_contains_article_tc_and_owner_role() -> None:
    def fail_delete(response):
        raise AssertionError("delete rejected")

    registry = BoardArticleCleanupRegistry(
        api_factory=FakeBoardApi,
        delete_assertion=fail_delete,
    )
    registry.track(303, object(), tc_id="API_BAD_B_001", owner_role="learner_a")

    with pytest.raises(BoardArticleCleanupError) as exc_info:
        registry.cleanup()

    message = str(exc_info.value)
    assert "board_article_id=303" in message
    assert "tc_id=API_BAD_B_001" in message
    assert "owner_role=learner_a" in message

