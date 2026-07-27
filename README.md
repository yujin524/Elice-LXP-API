# LXP QA - API 테스트 자동화

Elice LXP API를 Postman에서 검증한 뒤 pytest로 자동화한 프로젝트
로그인 → 토큰 발급 → 요청 전송 → 결과 리포트 생성까지 전부 코드로 처리

## 폴더 구조

```
200_project/
├── conftest.py                        # 전역 hook + 공용 fixture(인증/클라이언트/classroom_id 등)
├── pytest.ini                         # 실행 옵션·로깅·커스텀 마커
├── Jenkinsfile                        # CI 파이프라인 (prod/dev 실행 + Allure + 알림 + 로그 보관)
├── requirements.txt
├── .env / .env.dev                    # 운영·dev 계정·설정 (커밋 안 됨)
├── .env.example / .env.dev.example    # 작성용 템플릿
│
├── config/settings.py                 # 도메인 URL·org·timeout 등 설정값 (ENV_FILE로 .env/.env.dev 선택)
├── apis/                              # 도메인별 API 요청 빌더 (URL·파라미터 조립을 테스트에서 분리)
│   ├── course/                        # course, course_edu
│   ├── classroom/                     # classroom(학습현황), 게시판 경로
│   ├── classroom_edu/                 # classroom_edu 대시보드·구성원
│   ├── schedule_api/                  # schedule
│   └── org_board/                     # board(게시판)
├── utils/                             # ApiClient, 로그인 토큰 발급, 로거
│   └── notifyscripts/
│       ├── notify_discord.py          # CI 결과를 Discord webhook으로 요약 전송
│       └── notify_slack.py            # CI 결과를 Slack Incoming Webhook으로 요약 전송
│
└── tests/
    ├── api/
    │   ├── common/                    # 공용 검증 함수·파라미터(assertions.py, params.py, payload.py)
    │   ├── plugins/api_reporting.py   # 결과 요약 → 콘솔/Markdown/JSON 리포트 생성 플러그인
    │   ├── course/                    # 학습 과목 (운영)
    │   ├── course_edu/                # 교육자용 과목 편집·수업 관리 (dev 전용)
    │   ├── classroom/                 # 클래스 학습현황 조회 (운영)
    │   ├── classroom_edu/             # 교육자 대시보드·구성원 (dev 전용)
    │   ├── schedule/                  # 일정 조회·생성·수정·삭제
    │   └── board/                     # 게시판
    └── unit/                          # 리포팅 플러그인 등 자체 유틸 단위 테스트

reports/            # 실행 후 자동 생성 (.gitignore 대상): api-summary.md / api-summary.json
logs/               # pytest DEBUG 로그 (.gitignore 대상, Jenkins에서는 Artifact로 보관)
allure-results/, allure-report/   # Allure 원본·정적 리포트 (.gitignore 대상)
```

대부분의 `apis/` 모듈은 `ApiClient`로 요청을 보내고 response를 그대로 반환합니다.
별도 인증 URL이 필요한 로그인과 인증 없는 외부 페이지 확인은 `requests`를 직접 사용하지만,
공통 Logger 형식으로 요청·응답을 기록합니다. 검증(assert)은
`tests/api/common/assertions.py`의 함수나 테스트 자체가 담당해서 "어디로 보내는가"와
"무엇을 확인하는가"를 분리합니다.

```python
from apis.course.course_api import CoursePage

def test_next_lecture_page(api_client, course_id):
    resp = CoursePage(api_client).get_next_lecture_page(course_id=course_id)
    assert resp.status_code == 200
```

## 처음 한 번만 - 설치 & 계정 설정

```powershell
pip install -r requirements.txt
```

1. `.env.example`을 복사해 `.env`로 이름 변경 후 `ELICE_ID` / `ELICE_PW`만 채움
   (dev 전용 도메인을 돌리려면 `.env.dev.example` → `.env.dev`도 동일하게 준비)
2. 나머지 값(도메인 URL 등)은 비워두면 `config/settings.py`의 기본값이 적용

`.env` / `.env.dev`는 `.gitignore`에 등록되어 있어 Git에 올라가지 않음

> ⚠️ `config/settings.py`에는 절대 계정 정보를 직접 써넣지 말 것. 이 파일은 커밋 대상

## 실행 방법

기본적으로 모든 API 테스트는 `@pytest.mark.api`가 붙어 있어, **`RUN_LIVE_API_TESTS=1`이 없으면
자동 skip**(운영 서버에 실수로 요청이 나가는 것을 막기 위한 안전장치)

```powershell
$env:RUN_LIVE_API_TESTS='1'; pytest
```

### 운영 / dev 도메인 나눠서 실행

`course_edu`, `classroom_edu`, `board`와 일정 변경 테스트는 dev에서 실행합니다.
로컬에서는 아래처럼 `ENV_FILE`을 바꿔 실행할 수 있습니다. Jenkins는 `ENV_FILE` 대신
각 stage의 environment와 Jenkins Credentials로 prod/dev 설정을 분리합니다.

```powershell
# 운영 환경: course, classroom, schedule의 조회 중심 테스트
$env:ENV_FILE=''; $env:RUN_LIVE_API_TESTS='1'
pytest tests/api/course tests/api/classroom tests/api/schedule `
  --ignore=tests/api/schedule/positive/test_edit_schedule.py `
  --ignore=tests/api/schedule/positive/test_delete_schedule.py `
  --ignore=tests/api/schedule/validation/test_edit_schedule.py `
  --ignore=tests/api/schedule/validation/test_delete_schedule.py `
  --ignore=tests/api/schedule/positive/test_post_schedule.py `
  --ignore=tests/api/schedule/authentication/test_post_schedule.py `
  --ignore=tests/api/schedule/validation/test_post_schedule.py `
  --ignore=tests/api/schedule/scenario/test_schedule_create_read_delete.py

# dev 환경: course_edu, classroom_edu, board 전체 + schedule 변경 테스트
$env:ENV_FILE='.env.dev'; $env:RUN_LIVE_API_TESTS='1'
pytest tests/api/course_edu tests/api/classroom_edu tests/api/board `
  tests/api/schedule/positive/test_edit_schedule.py `
  tests/api/schedule/positive/test_delete_schedule.py `
  tests/api/schedule/validation/test_edit_schedule.py `
  tests/api/schedule/validation/test_delete_schedule.py `
  tests/api/schedule/positive/test_post_schedule.py `
  tests/api/schedule/authentication/test_post_schedule.py `
  tests/api/schedule/validation/test_post_schedule.py `
  tests/api/schedule/scenario/test_schedule_create_read_delete.py
```

특정 파일/케이스만 실행:
`pytest tests/api/course_edu/positive/test_course_get_positive.py::test_course_detail`

새 터미널을 열면 `ENV_FILE`이 초기화. 같은 터미널에서 되돌리려면 `$env:ENV_FILE=''`

> cmd를 쓴다면 `$env:X='y'` 대신 `set X=y`로 바꾸면 됨 (한 줄씩 실행)

## 인증 동작 방식

- `access_token` fixture가 세션당 한 번, `.env`(또는 `.env.dev`)의 계정으로 로그인해 토큰을 발급받음
- `api_client` fixture가 이 토큰 + org 헤더를 자동으로 붙인 클라이언트를 만듦
- 인증 실패 케이스(토큰 없음/빈 값/잘못된 값 등)를 검증할 때는 `api_client_factory`로
  특정 항목만 깨뜨린 클라이언트를 그때그때 만듦

## 결과 리포트

`tests/api/plugins/api_reporting.py`가 pytest 플러그인으로 등록되어 있어, 테스트가 끝나면 자동으로:

- 콘솔에 TC별 PASS/FAIL/SKIP/XFAIL/XPASS 및 그룹별 요약 표를 출력하고
- `reports/api-summary.md` (사람이 보기 좋은 표), `reports/api-summary.json` (raw 데이터)를 생성

각 테스트의 `@pytest.mark.tc(id=..., group=..., title=..., expected=...)` 마커 값이 리포트에
그대로 반영. **현재 TC 목록/그룹/기대값은 이 리포트가 항상 최신 기준**이므로, 이 문서에는
따로 TC 표를 두지 않음

`@pytest.mark.bug_candidate` + `@pytest.mark.xfail(reason=...)`가 같이 붙은 케이스는 "현재 동작과
기대 동작이 다름을 추적 중"이라는 뜻이며, 리포트에서 "Bug Candidates" 그룹 · XFAIL로 묶임

### Allure 리포트 (선택)

Scoop + Java + Allure CLI가 설치되어 있다면:

```powershell
allure serve allure-results          # 임시 웹 서버로 바로 확인
allure generate allure-results -o allure-report --clean && allure open allure-report  # 정적 리포트
```

설치가 안 되어 있다면:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
iwr -useb get.scoop.sh | iex
scoop bucket add java; scoop install temurin-lts-jdk
scoop install allure
```

## CI (Jenkins)

GitLab Integration, Webhook 또는 Jenkins Job에 설정된 trigger가 빌드를 시작하면
`Jenkinsfile`이 아래 순서로 실행됩니다. trigger 자체는 저장소 코드가 아니라
GitLab/Jenkins 관리 화면에서 설정합니다.

1. **Run API tests (prod)** — course_edu, classroom_edu, board 전체와 schedule 변경 테스트를 제외
2. **Run dev-only tests (dev)** — course_edu, classroom_edu, board 전체와 제외했던 schedule 변경 테스트
3. Allure 리포트 게시
4. prod/dev DEBUG 로그를 Jenkins Artifact로 보관
5. `utils/notifyscripts/notify_discord.py` — 통합 결과를 Discord webhook으로 전송
6. `utils/notifyscripts/notify_slack.py` — 통합 결과를 Slack Incoming Webhook으로 요약 전송

pytest는 터미널에 INFO 이상을 표시하고, 상세 요청·응답은 DEBUG 파일 로그에 기록합니다.
API 테스트가 실패하면 해당 테스트 로그가 Allure의 `실패 테스트 로그`로 첨부됩니다.
Jenkins에서는 `logs/api-tests-prod.log`, `logs/api-tests-dev.log`를 Artifact에서 받을 수 있습니다.

## 권한 테스트 계정 (Board 등)

Board 권한 경계 테스트는 아래 계정 값이 채워져 있는지로 실행 여부가 결정(값이 없으면
해당 역할이 필요한 테스트만 Skip). `.env.dev`에 채우면 됨

```dotenv
DEV_EDUCATOR_A_ID= / DEV_EDUCATOR_A_PW=
DEV_EDUCATOR_B_ID= / DEV_EDUCATOR_B_PW=
DEV_LEARNER_A_ID= / DEV_LEARNER_A_PW=
DEV_LEARNER_B_ID= / DEV_LEARNER_B_PW=
DEV_OUTSIDER_ID= / DEV_OUTSIDER_PW=
AUTHZ_CLASSROOM_ID=
ALLOW_PROD_AUTHZ_MUTATION_TESTS=false
```

- 계정 값을 넣었는데 로그인이 실패하면 설정 오류를 숨기지 않도록 **Fail** 처리(Skip 아님)
- 직접 prod pytest를 실행할 때 Board 권한/변경 테스트는 기본 Skip이며,
  `ALLOW_PROD_AUTHZ_MUTATION_TESTS=1`로 명시적으로 허용할 수 있음
- Jenkins prod stage는 `tests/api/board` 전체를 `--ignore`하므로 위 값을 켜도 Board를 실행하지 않음
- `RUN_LIVE_API_TESTS=1`이 없으면 계정 준비 여부와 관계없이 전부 Skip되는 건 동일

## 자주 나오는 문제

| 증상 | 원인 / 해결 |
|---|---|
| 전부 SKIPPED로만 나옴 | `RUN_LIVE_API_TESTS` 환경변수를 안 켰을 가능성이 큼. 위 "실행 방법" 참고 |
| ".env에 ELICE_ID, ELICE_PW가 설정되지 않았습니다" | `.env` 파일이 없거나 값이 비어있음 |
| 로그인 실패 (`RuntimeError: 로그인 요청 실패`) | 계정 정보가 틀렸거나 `AUTH_URL` 응답 형식이 바뀜 — `utils/auth_token.py`의 `get_token()` 확인 |
| 401/403이 대부분 실패로 뜸 | 계정 권한 문제이거나 해당 classroom/course 접근 권한이 없는 계정 |
| `pytest`가 "명령을 찾을 수 없음" | `python -m pytest ...`로 실행 |
