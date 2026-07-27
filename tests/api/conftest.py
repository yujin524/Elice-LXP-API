"""tests/api 공통 conftest.

모든 도메인(board, classroom, classroom_edu, course, course_edu, schedule)의
API 테스트에 자동 적용되는 공통 fixture를 둔다.

- _log_api_calls: 각 테스트 동안 모든 API 요청/응답을 자동 로깅
  (구현은 utils.logger.install_api_call_logging, ApiClient.request를 monkeypatch로 감싼다.
   테스트가 끝나면 자동 원복되고, 공용 utils/api_client.py는 수정하지 않는다.)
- _attach_failure_log_to_allure: 실패한 테스트의 마스킹된 로그를 Allure에 첨부
"""

import io
import logging
import pytest
from utils.logger import SecretRedactingFilter, install_api_call_logging, install_secret_redaction

logger = logging.getLogger("tests.api")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """fixture teardown에서 테스트 실패 여부를 확인할 수 있게 report를 저장합니다."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def _attach_failure_log_to_allure(request):
    """실패한 API 테스트의 해당 테스트 로그만 Allure에 첨부합니다."""
    install_secret_redaction()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    handler.addFilter(SecretRedactingFilter())
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    yield

    root_logger.removeHandler(handler)
    handler.close()
    report = getattr(request.node, "rep_call", None)
    captured_log = stream.getvalue().strip()
    if report is None or not report.failed or not captured_log:
        return

    try:
        import allure
        allure.attach(captured_log, name="실패 테스트 로그", attachment_type=allure.attachment_type.TEXT)
    except Exception as exc:
        logger.warning("Allure 실패 로그 첨부를 건너뜁니다: %s", exc)


@pytest.fixture(autouse=True)
def _log_api_calls(monkeypatch):
    """모든 API 테스트에서 요청/응답을 자동 로깅한다. (전 도메인 공통)"""
    install_api_call_logging(monkeypatch, logger)
