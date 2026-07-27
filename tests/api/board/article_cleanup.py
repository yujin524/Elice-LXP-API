"""Board 자동화 테스트가 생성한 게시글의 식별 및 정리 도구."""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4
from apis.org_board.org_org_board_article import OrgBoardArticleApi
from tests.api.common.assertions import assert_board_article_delete_success
from tests.api.common.payload import board_article_delete_data


logger = logging.getLogger(__name__)

BOARD_AUTOMATION_TITLE_PREFIX = "[QA-AUTO][AUTHZ]"


def build_automation_article_title(tc_id: str = "UNASSIGNED") -> str:
    """화면에서도 출처를 식별할 수 있는 고유 테스트 게시글 제목을 만듭니다."""
    return f"{BOARD_AUTOMATION_TITLE_PREFIX}[{tc_id}][{uuid4().hex[:8]}]"


@dataclass(frozen=True)
class BoardArticleCleanupTarget:
    """작성자 클라이언트와 함께 보관하는 게시글 정리 대상."""

    article_id: int
    owner_client: Any
    tc_id: str
    owner_role: str


class BoardArticleCleanupError(AssertionError):
    """하나 이상의 자동화 게시글을 정리하지 못했을 때 발생합니다."""


class BoardArticleCleanupRegistry:
    """테스트가 생성한 게시글만 추적하고 작성자 권한으로 정리합니다."""

    def __init__(
        self,
        *,
        api_factory: Callable[[Any], Any] = OrgBoardArticleApi,
        delete_assertion: Callable[[Any], Any] = assert_board_article_delete_success,
    ) -> None:
        self._targets: dict[int, BoardArticleCleanupTarget] = {}
        self._api_factory = api_factory
        self._delete_assertion = delete_assertion

    def track(
        self,
        article_id: int,
        owner_client: Any,
        *,
        tc_id: str = "UNASSIGNED",
        owner_role: str = "unknown",
    ) -> int:
        """생성 직후 게시글을 정리 대상으로 등록하고 ID를 그대로 반환합니다."""
        self._targets[article_id] = BoardArticleCleanupTarget(
            article_id=article_id,
            owner_client=owner_client,
            tc_id=tc_id,
            owner_role=owner_role,
        )
        logger.info(
            "[정리등록] board_article_id=%s tc_id=%s owner_role=%s",
            article_id,
            tc_id,
            owner_role,
        )
        return article_id

    def mark_deleted(self, article_id: int) -> None:
        """테스트 본문에서 정상 삭제된 게시글을 정리 대상에서 제외합니다."""
        self._targets.pop(article_id, None)

    def cleanup(self) -> None:
        """남은 게시글을 각각의 작성자 클라이언트로 삭제합니다."""
        cleanup_errors: list[str] = []

        for target in tuple(self._targets.values()):
            try:
                response = self._api_factory(target.owner_client).post_delete_article(
                    data=board_article_delete_data(board_article_id=target.article_id),
                )
                self._delete_assertion(response)
                self._targets.pop(target.article_id, None)
                logger.info(
                    "[정리완료] board_article_id=%s tc_id=%s owner_role=%s",
                    target.article_id,
                    target.tc_id,
                    target.owner_role,
                )
            except Exception as exc:
                logger.exception(
                    "[정리실패] board_article_id=%s tc_id=%s owner_role=%s",
                    target.article_id,
                    target.tc_id,
                    target.owner_role,
                )
                cleanup_errors.append(
                    f"board_article_id={target.article_id}, "
                    f"tc_id={target.tc_id}, owner_role={target.owner_role}: {exc}"
                )

        if cleanup_errors:
            raise BoardArticleCleanupError(
                "Board 자동화 게시글 정리 실패: " + "; ".join(cleanup_errors)
            )

