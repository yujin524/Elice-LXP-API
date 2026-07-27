"""API 에러 코드/상태 공통 모듈.

여러 테스트 파일에 흩어져 있던 에러 코드 문자열과 인증 실패 상태코드 세트를
한곳에 모아둡니다. 서버 응답의 에러 코드/타입이 바뀌면 여기만 고치면 됩니다.
"""
from __future__ import annotations


# 인증 실패 시 서버가 돌려줄 수 있는 HTTP 상태 코드
# (Authorization 헤더 없음 / 빈 값 / 공백 / 잘못된 토큰 케이스 공통)
AUTH_FAILURE_STATUSES = {401, 403, 409}

# 응답 body의 "code" 필드에 담기는 에러 코드
ERROR_CODE_MODEL_NOT_FOUND = "model_not_found"  # 존재하지 않는 리소스 조회 (409)
ERROR_CODE_UNEXPECTED_RESULT = "elice_core_unexpected_result"  # 인증/헤더 이상 등 (409)

# 422 응답 body의 detail[].type 필드에 담기는 pydantic validation 에러 타입
ERROR_TYPE_MISSING = "missing"  # 필수 쿼리/path 파라미터 누락
ERROR_TYPE_UUID_PARSING = "uuid_parsing"  # UUID 형식이 아닌 값

# api-rest(REST_BASE_URL) 계열 인증 실패 시 detail.resp_json.fail_code
FAIL_CODE_NO_ACCOUNT_API_SESSION = "no_account_api_session"


# utils/auth_token.py의 로그인 관련 에러 메시지 템플릿
LOGIN_REQUEST_FAILED = "로그인 요청 실패: {exc}"
LOGIN_FAILED = "로그인 실패 (status={status}): {body}"
LOGIN_RESPONSE_JSON_PARSE_FAILED = "로그인 응답 JSON 파싱 실패: {body}"
LOGIN_ACCESS_TOKEN_MISSING = "응답에 access_token이 없습니다: {body}"
LOGIN_ENV_CREDENTIALS_MISSING = (
    ".env에 ELICE_ID, ELICE_PW가 설정되지 않았습니다. "
    ".env.example을 참고해 값을 채워주세요."
)
