# Elice LXP API QA Automation

> **Team Project / Personal Contribution README**  
> **담당 영역:** Schedule API · Allure Reporting  
> **기간:** 2026.07.08 ~ 2026.07.22  
> **협업:** Notion · Discord · GitLab  
> **기술:** Python · pytest · Requests · Postman · Allure

---

## 1. 프로젝트 소개

Elice LXP의 API를 분석하고 Postman으로 사전 검증한 뒤 pytest 기반 자동화 테스트로 전환한 팀 프로젝트입니다.

저는 전체 API 영역 중 **Schedule API 테스트 설계·자동화**와 **Allure 리포팅 구조 개선**을 담당했습니다.

담당 범위에서는 단순 상태코드 확인을 넘어 **필수값·경계값·인증·권한·오류 Body·ICS 응답·시나리오 테스트·cleanup**까지 검증했습니다.

---

## 2. 담당 범위

| TC 구간 | 대상 | 주요 검증 |
|---|---|---|
| API_CS_001~011 | `GET /schedule` | 정상 조회, count 경계, 필수값 누락, 날짜 역전, 인증·조직 헤더, UUID 오류 |
| API_CS_012~016 | `GET /schedule/count` | 정상 개수, 필수값, 날짜 범위, 인증, UUID |
| API_CS_017~020 | `GET /schedule/ics` | ICS 정상 응답, 필수값, 인증, UUID |
| API_CS_021~023 | 강의실 상세 조회 | 정상 조회, `lectureroom_id` 누락, Authorization 누락 |
| API_CS_024~029 | `POST /schedule` | 정상 생성, org 헤더, 필수 Body, 권한 경계 |
| API_CS_030 | 일정 시나리오 | 생성 → 조회 → 삭제 + cleanup |

> **개인 담당 범위: API_CS_001 ~ API_CS_030, 총 30개 TC**  
> Schedule 영역의 추가 테스트는 팀원이 담당했습니다.

---

## 3. Postman 사전 검증

자동화 코드를 작성하기 전에 브라우저 Network 요청과 API 명세를 확인하고 **Postman에서 실제 요청/응답을 먼저 검증**했습니다.

### 확인 항목

- HTTP Method / Endpoint
- Authorization Header
- `x-elice-org-name-short`
- `classroom_id`
- `dt_start_ge`
- `dt_start_le`
- `count`
- `offset`
- HTTP Status Code
- JSON Response Body
- ICS `Content-Type`
- 명세와 실제 서버 응답 차이

### 진행 흐름

```text
브라우저 Network 확인
        ↓
API 명세와 요청값 비교
        ↓
Postman 요청 구성
        ↓
정상 / 예외 응답 확인
        ↓
TC 작성
        ↓
pytest 자동화
```

Postman 결과를 그대로 자동화하는 것이 아니라, **기대 결과와 실제 응답을 먼저 비교한 뒤 테스트 케이스로 구체화**했습니다.

---

## 4. 테스트 구조

목적별로 테스트를 분리했습니다.

```text
tests/api/schedule/
├─ positive/
├─ validation/
├─ authentication/
├─ boundary/
└─ scenario/
```

- `positive` : 정상 동작
- `validation` : 필수값, 형식, 범위
- `authentication` : 토큰 / 조직 헤더
- `boundary` : 경계값 및 특수 데이터
- `scenario` : 생성 → 조회 → 삭제 흐름

테스트 목적이 파일 구조에서도 바로 드러나도록 구성해 실패 위치를 빠르게 확인할 수 있게 했습니다.

---

## 5. Response Validation

### JSON 응답

HTTP Status만 확인하지 않고 Body 내부 값도 검증했습니다.

- 응답 타입
- 요청한 `count`에 따른 반환 개수
- 필수값 누락 시 `detail.type=missing`
- 오류 위치 `detail.loc`
- 날짜 범위 오류 코드
- 내부 오류 코드
- UUID Parsing 오류
- 존재하지 않는 모델 오류

### ICS 응답

`GET /schedule/ics`는 JSON이 아닌 캘린더 텍스트 응답이므로 별도 기준을 적용했습니다.

- HTTP 200
- `Content-Type` 확인
- `BEGIN:VCALENDAR`
- `END:VCALENDAR`
- 일정 존재 시 `VEVENT`

응답 형식에 맞게 검증 방법을 분리했습니다.

---

## 6. Scenario & Cleanup

`API_CS_030`에서는 단일 API가 아닌 실제 일정 흐름을 검증했습니다.

```text
일정 생성
   ↓
일정 목록 조회
   ↓
생성 데이터 확인
   ↓
일정 삭제
```

### 구현 포인트

- UUID를 포함한 고유 summary 생성
- summary와 시작 시간으로 생성 데이터 식별
- 생성된 `schedule_id` 추적
- 중간 Assertion 실패 시에도 `finally`에서 cleanup 수행

**테스트 실패가 다음 테스트의 데이터에 영향을 주지 않도록 정리 로직까지 포함**했습니다.

---

## 7. Allure Reporting 개선

### 문제

각 테스트마다 다음 메타데이터를 반복 작성하면 TC가 늘어날수록 유지보수 부담이 커졌습니다.

```python
@allure.epic("Schedule API")
@allure.feature("GET /schedule")
@allure.story("Validation")
@allure.title("[API_CS_003] classroom_id 누락")
```

### 개선

`pytest.mark.tc(id, group, title, expected)` 정보를 기준으로 Allure 메타데이터를 자동 생성하도록 구조를 변경했습니다.

```text
pytest.mark.tc
      ↓
build_allure_metadata()
      ↓
apply_allure_metadata()
      ↓
Allure Title / Story / Description / TC ID
```

### 결과

- 반복 Allure 데코레이터 **112줄 제거**
- 공통 로직 **34줄로 통합**
- 순 코드 **78줄 감소**
- 관련 메타데이터 코드 약 **70% 축소**
- TC 정보를 수정하면 pytest 결과와 Allure에 동일하게 반영

이후 팀 공통 `allure_metadata.py` 플러그인 구조로 확장되었습니다.

---

## 8. Troubleshooting

### 8-1. 명세와 실제 응답이 다른 문제

**문제**  
명세에서 기대한 HTTP Status와 실제 서버 응답이 다른 케이스가 존재했습니다.

**해결**

다음 정보를 분리해서 관리했습니다.

- 명세상 Expected
- 실제 HTTP Status
- 실제 Response Body
- 결함 후보 여부
- 자동화 테스트 처리 방식

필요한 경우 `xfail(strict=True)`로 유지해 서버 동작이 수정되면 `XPASS`로 드러나도록 했습니다.

**결과**  
테스트 실패를 단순 코드 오류로 처리하지 않고 **명세 이슈와 서버 결함 후보를 구분해서 관리**할 수 있었습니다.

### 8-2. ICS 응답 검증 방식 분리

**문제**  
일반 JSON API와 동일한 방식으로 파싱할 수 없었습니다.

**해결**  
`Content-Type`, `VCALENDAR`, `VEVENT`를 기준으로 전용 검증 로직을 적용했습니다.

**결과**  
API 응답 포맷에 맞는 검증 전략을 적용했습니다.

### 8-3. Scenario 실패 후 테스트 데이터가 남는 문제

**문제**  
생성 이후 테스트가 실패하면 일정 데이터가 서버에 남을 수 있었습니다.

**해결**  
생성된 ID를 추적하고 `finally`에서 삭제하도록 cleanup을 구성했습니다.

**결과**  
반복 실행 시 데이터 간섭을 줄였습니다.

---

## 9. Bug Report

### Authorization 누락인데 HTTP 200 반환

강의실 상세 조회 API에서 Authorization Header를 제거했을 때 다음 응답을 확인했습니다.

**Expected**

- HTTP 403 Forbidden

**Actual**

- HTTP 200
- Body 내부 `status_code=403`
- `fail_code=no_found_sessionkey`

**Risk**

클라이언트나 모니터링 시스템이 HTTP Status만 확인할 경우 인증 실패 요청을 성공으로 판단할 수 있습니다.

**처리**

- Jira Bug Report 작성
- 요청 조건과 Response Body 기록
- 기대 결과 / 실제 결과 비교
- 자동화 테스트에서 `xfail(strict=True)`로 추적

---

## 10. 성과

| 항목 | 결과 |
|---|---:|
| 담당 TC | 30개 |
| Allure 반복 코드 | 112줄 |
| 공통 메타데이터 로직 | 34줄 |
| 순 코드 감소 | 78줄 |
| 관련 메타데이터 코드 축소 | 약 70% |
| 대표 결함 | Authorization Status 불일치 |

Schedule API의 정상·예외·인증·경계·시나리오 테스트를 자동화했고, HTTP Status뿐 아니라 중첩 오류 Body와 ICS 포맷까지 검증했습니다.

---

## 11. 담당 파일

```text
apis/schedule_api/
tests/api/schedule/
tests/api/schedule/conftest.py
tests/api/plugins/allure_metadata.py
conftest.py
pytest.ini
```

---

## 12. Test Evidence 

본 프로젝트는 교육기관에서 임시 제공한 API 도메인을 사용했으며, 현재 해당 도메인이 종료되어 실시간 실행이 어렵습니다.

그래서 당시 수행 내용을 확인할 수 있도록 **실행 영상 링크**를 별도로 제공합니다.

### 실행 영상

- **YouTube API 테스트 실행 영상:** `https://youtu.be/GEX4QX6ESck`

---

## 13. 실행 유의사항

본 프로젝트는 교육기관의 임시 테스트 도메인과 계정으로 진행했습니다.  
현재 도메인이 종료되어 실시간 API 테스트를 그대로 재실행할 수 없습니다.

외부 공개 저장소에는 `.env`, 인증 토큰, 테스트 계정 등 민감 정보를 포함하지 않습니다.
