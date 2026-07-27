"""classroom(클래스 홈 미리보기) API 테스트 전용 fixture 모음."""

import pytest
from apis.classroom.classroom_id import ClassroomPage


@pytest.fixture
def classroom_page(api_client):
    """정상 Authorization 헤더와 org 헤더가 포함된 ClassroomPage."""
    return ClassroomPage(api_client)
