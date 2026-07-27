# 게시글 목록 조회 GET /classroom/{classroom_id}/article API 테스트 — API_AR_001

import logging
import pytest
from apis.classroom.classroom_classroom_id_article import get_article_list
from tests.api.common.params import board_article_list_params
from tests.api.common.assertions import assert_article_list

logger = logging.getLogger(__name__)

API_AR_001_TC = dict(id="API_AR_001", group="Positive", title="게시글 목록 정상 조회", expected="200, JSON 배열, 필수 필드 존재")

@pytest.mark.api
@pytest.mark.requires_token
@pytest.mark.tc(**API_AR_001_TC)
def test_get_article_list_success(api_client, classroom_id):
    """
    TC ID: API_AR_001
    시나리오: 학습자 권한으로 본인 전용 게시글 목록 조회(GET) API를 호출하면
    200 상태 코드와 정상적인 게시글 목록(JSON 배열)이 반환되어야 한다.
    """
    response = get_article_list(api_client, classroom_id=classroom_id, params=board_article_list_params())

    logger.info("[API 요청] %s %s", response.request.method, response.request.url)

    assert_article_list(response, classroom_id, max_count=10)
