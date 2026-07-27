"""인증 실패(깨진 client) 파라미터화 테스트 공통 케이스.

course / course_edu의 "인증 헤더 없음 / 빈 토큰 / 공백 토큰 / 잘못된 토큰" 4종 네거티브
테스트가 파일마다 같은 BROKEN_CLIENTS 리스트를 반복 정의하고 있어서 한 곳으로 모은다.
"""

from __future__ import annotations

import pytest


class AuthNegativeCases:
    """인증 실패 4종 케이스와 기대 상태 코드를 제공하는 공용 헬퍼."""

    STATUS_CODES = {401, 403, 409}

    CASES = [
        pytest.param({"include_auth": False}, id="no_auth"),          # Authorization 헤더 없음
        pytest.param({"access_token": ""}, id="empty_token"),         # Bearer (빈 값)
        pytest.param({"access_token": "  "}, id="blank_token"),       # Bearer (공백)
        pytest.param({"access_token": "invalid-token"}, id="invalid_token"),  # 잘못된 토큰
    ]

    @classmethod
    def parametrize(cls, argname: str = "client_kwargs"):
        """@AuthNegativeCases.parametrize() 로 4종 케이스를 그대로 파라미터화한다."""
        return pytest.mark.parametrize(argname, cls.CASES)
