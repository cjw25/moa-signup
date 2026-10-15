# 모아 · 회원가입 프로젝트

## Day3 실제 HTTP 요청 관찰 미니프로젝트

이 저장소의 기존 Day2 일반 게시판(`general/`)과 감시 API(`monitor/backend/`), 감시 Next 화면(`monitor/next-frontend/`)을 이어서 사용한다. 기존 게시글·계정·메모·DB 볼륨은 지우지 않는다. 이번 변경은 요청 수집, `http_events` 저장, 실제 기록 캡처, 정규화·조회 선택, 60초 분석 API, 화면의 HTTP 카드다. 외부 클라우드 배포는 진행하지 않았다.

### 구성과 데이터 흐름

`general/app.py`의 `create_app()`이 `register_request_logging(app)`을 호출하고, `general/request_logging.py`가 `@app.after_request`에 `record_request`를 등록한다. 이 함수는 응답의 방법·경로·상태를 JSON으로 **표준 출력에 print**하고, 별도로 `MONITOR_URL`에 `X-Event-Token: EVENT_TOKEN`을 붙여 POST한다. 출력만 성공해도 감시 DB 저장이 성공했다는 뜻은 아니다. `/health`는 자동 점검 트래픽이 실습 기록에 섞이지 않도록 제외한다. `compose-general.yaml`의 `MONITOR_URL`은 감시 API의 `/api/events`를 가리키고, 두 Compose의 `EVENT_TOKEN` 값이 일치해야 한다.

감시의 `routes/events.py:receive_event()`가 토큰·형식을 검증하고 `event_rules.py:make_event()`가 `GET /`의 `200`을 `post_list`, `/training-missing`의 `404`를 `request_error`로 분류한다. 기존 `login_failure`/`login_success`도 유지한다. `repositories/events.py:create_event()`는 감시 DB의 `http_events`에 넣고, **DB가 ID와 `occurred_at`을 수신·저장 시각으로 부여한다**. 일반 앱의 JSON `timestamp`는 전송 진단용이며 분석 기준시각이 아니다. 기존 볼륨의 `request_events`는 첫 접근 때 `http_events`로 이름을 바꿔 행을 보존한다. `general_users`, `posts`, `monitor_users`, `observation_notes`는 그대로 둔다.

`learning/capture_case.py`는 로컬 일반 서비스에 로그인한 뒤 목록 GET을 지정 횟수만큼, 마지막에 `/training-missing` GET을 한 번 실제로 보낸다. 로그인 기록 다음의 DB ID를 경계로 잡아 이번 저장 행을 읽는다. 미리 만든 JSON이나 SQL INSERT로 요청을 대신하지 않는다. `learning/normalize.py:normalize_event()`는 원본 딕셔너리를 복사해 숫자 ID를 `http-원본ID`로 바꾸고 `source=http_live`, `kind=event_type`을 더한다. 방법·경로·상태·수신시각은 유지하며 없는 IP·사용자 필드를 만들지 않는다. 404도 이 단계에서는 남는다.

`learning/http_rules.py:select_views()`는 **GET, 경로 `/`, 상태 200, 종류 `post_list`** 네 조건을 모두 만족하는 행 목록을 반환한다. 그 목록의 길이가 조회 횟수이고 같은 목록의 ID가 조회 근거다. `find_following_errors()`는 마지막 조회의 DB 수신시각 뒤 `0 < 간격 <= 30초`인 404를 전체 정규화 행에서 찾아 문맥 근거에만 더한다. 조회가 없으면 뒤따른 404도 없다. `assess()`는 `count >= threshold`로 판정한다. 따라서 통제한 12회 조회와 404 한 건의 **관찰값은 12, 근거는 13행**이다.

`routes/analysis.py`의 로그인 보호 API는 새 관찰 때 현재 최대 ID만 저장하고 기존 행을 삭제하지 않는다. 결과 조회는 그 ID 이후이며 **첫 결과 요청의 기준시각으로부터 과거 60초**에 감시 DB가 받은 행을 `learning/support.py`에서 읽는다. 시작 버튼부터 60초를 자동 수집하는 타이머는 아니다. `learning/report.py:build_report()`가 같은 행으로 HTTP 카드 한 개의 관찰값·기준·판정·이유·`evidence` ID·`records`를 만든다. `components/AnalysisClient.js`는 새 관찰·기준 입력·결과 불러오기·근거 표를 연결한다. 기준 10에서 20으로 바꿔도 기존 `after_id`와 `reference_time`을 다시 보내므로 근거와 관찰값이 같다. 새 관찰을 누르면 화면의 이전 기준시각과 결과를 지운다. 표의 `http-` 뒤 숫자가 원본 DB ID다. 404는 같은 서비스에서 시간상 뒤따른 기록일 뿐 동일 사용자·IP, 인과관계나 침해를 입증하지 않는다. 기준 미해당도 정상이라는 증명이 아니다.

### 로컬 실행과 확인 순서 (Windows CMD)

저장소 루트에서 기존 일반·감시 DB와 계정을 준비한다. 첫 실행이면 `docker network create m5d1-events` 후 두 Compose를 `up -d --build`로 실행하고, 각 앱 폴더의 `create_user.py`로 계정을 만든다. 기존 볼륨이 있으면 `down -v`를 사용하지 않는다. 루트의 **Git에 넣지 않는** `.env`에 기존 일반 게시판 계정의 `CAPTURE_USERNAME`, `CAPTURE_PASSWORD`를 설정한다. `compose-monitor.yaml`이 두 값을 monitor-api 컨테이너에 넘긴다. 실제 비밀번호·세션 키·토큰은 제출하지 않는다.

```cmd
if not exist monitor\backend\learning\data mkdir monitor\backend\learning\data
docker compose -f compose-monitor.yaml up -d --build
docker compose -f compose-general.yaml up -d --build
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 4 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson2
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson3
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson4 10
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson5
```

각 명령이 성공한 다음 명령으로 넘어간다. `-T`와 `>`는 컨테이너의 JSON 출력을 PC 임시 파일에 저장하고, 성공했을 때만 `observation.json`으로 바꾼다. `learning/data`는 monitor-api에 읽기 전용으로 연결되어 있어 수업 파일 실습 네 개가 **같은 파일**을 읽는다. 실행 생성 JSON은 Git에서 제외한다. 4회 캡처의 예상은 원본 5행, 정규화 5행, 선택한 조회 4행, 기준 10 미해당이다. 실패하면 이전 `observation.json`을 이번 결과로 간주하지 않는다.

감시 화면 `http://localhost:8082`에서 로그인하고 기준 10으로 **새 관찰 시작**을 누른 뒤 아래를 실행한다. 다른 탭에서 일반 게시판을 새로고침하지 않는다. 요청 뒤 **1분 이내에 처음 결과 불러오기**를 누른다. 그 결과의 기준시각이 고정된다.

```cmd
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 12 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
```

예상 결과는 관찰값 12·기준 10·검토 후보, 조회 근거 12행과 뒤따른 404 한 행의 합계 13행이다. **새 관찰을 누르지 않고** 기준만 20으로 바꿔 결과를 다시 불러오면 같은 `after_id`·기준시각·근거 ID에서 관찰값 12·기준 미해당이 예상된다. 기준 10으로 되돌려 결과를 불러오면 다시 검토 후보가 예상된다. 새 관찰을 시작하고 일반 요청을 보내지 않으면 관찰값 0·근거 없음이 예상되며 이전 DB 행은 남는다. 결과 화면은 JSON 파일이 아니라 감시 DB를 직접 읽는다.

오류·예상과 다른 개수·60초 경과가 있으면 일반 앱의 전송 경고, 감시 API 로그와 아래 원본 DB 행을 확인한다. 원인을 고친 뒤 **새 관찰 시작 → 캡처 → 1분 안의 첫 결과** 순으로 다시 진행한다. 숫자를 맞추려고 DB나 볼륨을 지우거나 JSON을 편집하지 않는다.

```cmd
docker compose -f compose-general.yaml logs --tail 20 general-api
docker compose -f compose-monitor.yaml logs --tail 20 monitor-api
docker compose -f compose-monitor.yaml exec monitor-db psql -U monitor -d monitor_db -c "SELECT id, occurred_at, method, path, status_code, event_type FROM http_events ORDER BY id DESC LIMIT 15;"
```

### 예상값과 실제 확인 상태

| 상황 | 예상값 | 현재 확인 |
|---|---|---|
| 4회 + 404, 파일 실습 기준 10 | 정규화 5행, 조회 4행, 미해당 | Docker CI 통과; 개인 계정 로컬 실습 미확인 |
| 10회 + 404, 화면 기준 10 | 관찰값 10, 검토 후보, 근거 11행 | Docker CI 통과; 개인 계정 로컬 실습 미확인 |
| 12회 + 404, 화면 기준 10 | 관찰값 12, 검토 후보, 근거 13행 | PostgreSQL·Docker CI 통과; 개인 계정 로컬 실습 미확인 |
| 같은 구간 기준 20 | 관찰값·근거 ID 유지, 기준 미해당 | PostgreSQL·Docker CI 통과; 개인 계정 로컬 실습 미확인 |
| 새 관찰 뒤 무요청 | 관찰값 0, 기존 DB 행 보존 | PostgreSQL·Docker CI 통과; 개인 계정 로컬 실습 미확인 |

### 선택 실습

- **PCAP 분리:** `python -m learning.pcap_exercise`는 자체 생성한 교육용 PCAP에서 처음 5초의 패킷 4개·바이트 34, 처음 1초의 패킷 2개·바이트 18을 계산한다. 시간 폭을 줄이면 뒤의 두 패킷이 제외된다. 실제 게시판 캡처가 아니며 HTTP 카드에 섞지 않는다.
- **IOC 일치:** `python -m learning.ioc_exercise`는 문서용 IP `203.0.113.10`의 일치와 `198.51.100.7`의 불일치를 보여 준다. 실제 `http_events`에는 IP 열이 없으므로 이 결과로 요청자나 사용자를 식별하지 않는다.
- **기준 경계:** 기준 10으로 새 관찰을 시작하고 아래 명령을 실행해 1분 이내 결과를 읽으면 `10 >= 10`이므로 검토 후보, 조회 10행 + 404 1행 = 근거 11행이다. Docker CI가 이 실제 요청과 DB 근거 ID의 일치를 검증했다. 다음에는 **다시 새 관찰 시작**을 누르고 위의 `capture_case 12` 명령으로 기본 사례를 만든다. 데이터 삭제는 필요 없다.
- **AI 후보 코드 검토:** 아래 순수 함수 후보를 현재 구현과 대조했다. `status_code == 404`를 조회 횟수에 더하고 GET·경로·상태·종류의 네 조건을 빠뜨려 거절했다. 마지막 조회 뒤 30초의 문맥 선택도 없으므로 `find_following_errors()`를 따로 써야 한다. `count > threshold`이면 정확히 10회·기준 10을 놓치므로 현재의 `>=`를 채택했다. 후보는 근거 ID를 계산하지 않으므로 현재처럼 같은 `select_views()` 목록에서 개수와 ID를 함께 구한다. 이는 코드 비교이며 모델 API를 호출하거나 실제 로그·비밀값을 외부에 보내지 않았다.

```cmd
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 10 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
```

```python
def candidate(events, threshold):
    count = sum(event["path"] == "/" or event["status_code"] == 404 for event in events)
    return count > threshold
```


## Day2 일반·감시 미니프로젝트

기존 Day1 Flask 게시판(`general/`), Flask 감시 API(`monitor/backend/`), 감시 Next.js 화면(`monitor/next-frontend/`)을 `day2-deploy` 브랜치에서 배포용으로 연결했습니다. 세 앱의 Render 설정, 별도 Supabase DB, 서버 프록시, Sentry 및 오류 수정 내역은 [deployment-plan.md](deployment-plan.md)를 보세요. 이 저장소의 기존 회원가입 프로젝트는 아래 설명대로 유지됩니다.

이번 작업은 Flask Dockerfile의 Waitress 실행, 환경 변수 기반 DB 연결과 배포 SQL, 기록 토큰 검증, Next Route Handler의 쿠키 전달, 앱 초기화 시 Sentry 설정, 실습 오류 수정을 포함합니다. 현재 외부 서비스는 **미배포**이며 실제 배포 URL과 Sentry 수신은 확인되지 않았습니다. 작업 커밋은 `5248d81`(통합 준비), `1becad4`(오류 수정), `65a7ec3`(문서화), `6956ba4`(프록시 204 응답 수정)입니다.

### Day2 선택 항목 확인

**1. 감시 API 주소·DB·입력 오류 구분.** 감시 화면에서 `/api/...` 호출이 `503`이고 `감시 API 주소가 설정되지 않았습니다.`가 보이면 Next 서버의 `MONITOR_API_URL` 누락이다. `502`와 `감시 API에 연결하지 못했습니다. 잠시 후 다시 불러와 주세요.`가 보이면 `monitor/next-frontend/app/api/[...path]/route.js`가 감시 Flask에 연결하지 못한 것이다. Next 서비스 로그와 `MONITOR_API_URL`의 HTTPS 기준 주소, 감시 Flask의 실행 상태를 먼저 확인한다. 일반 Flask의 기록 전송만 실패하면 `general/request_logging.py`의 `감시 서버 전송 실패` 경고, `MONITOR_URL`의 `/api/events` 접미사, 양쪽 `EVENT_TOKEN`을 확인한다. 감시 Flask가 실제로 응답한 `400`·`401`·`403`·`500`은 프록시가 상태 코드를 유지하므로 `502`와 구분된다.

DB 오류는 일반 게시글 또는 감시 메모·기록의 조회·저장 시 나타난다. 해당 Flask 서비스 로그의 PostgreSQL 예외와 **그 앱의** `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE`를 확인한다. 일반 DB와 감시 DB는 다른 Supabase 프로젝트다. 잘못된 입력은 감시 `routes/auth.py`, `routes/events.py`, `routes/notes.py`가 JSON `message`와 `400` 또는 인증 실패 `401`을 반환하고, 일반 게시글 `routes/posts.py`는 입력 오류를 화면에 `400`으로 표시한다. 이때는 DB 주소를 바꾸기 전에 입력값과 API 응답을 확인한다. 두 Flask의 `/health`는 `app.py`에서 DB 조회 없이 `{"status":"ok"}`를 반환하는 **프로세스 확인**이다. 따라서 `/health`가 `200`이어도 DB 접속·계정 로그인·메모 저장 성공을 뜻하지 않는다. 로그인과 DB CRUD를 별도로 실행해 확인한다.

**2. Next 연결 실패 안내와 재시도.** `monitor/next-frontend/app/api/[...path]/route.js`는 `MONITOR_API_URL`이 없을 때 JSON `message`와 `503`, 연결 예외일 때 JSON `message`와 `502`를 반환한다. `lib/api.js`는 실패 응답의 `message`와 `status`를 Error에 담고, `components/MemoDashboard.js`의 `report()` 또는 초기 로그인 상태 확인의 `catch`가 이를 `role="alert"`로 표시한다. 로그인 화면에서는 주소를 고친 후 **로그인**을 다시 누른다. 로그인 중인 화면에서는 `components/EventList.js`의 **기록 불러오기** 또는 메모 목록의 **새로고침**을 누르면 `refreshEvents()`/`refresh()`가 API를 다시 호출하고 이전 오류 문구를 지운다. 실제 API가 보낸 `400`·`401` 등은 프록시가 그대로 전달한다.

**3. Sentry 자료 제외.** 두 Flask의 `observability.py`는 `send_default_pii=False`로 기본 사용자 정보 전송을 끄고 `max_request_body_size="never"`로 요청 본문 자동 수집을 막는다. 추가로 `before_send=remove_private_data`가 전송 직전 최상위 `user`를 삭제하고, `request`의 `data`(본문), `cookies`(세션 쿠키), `headers`(인증 헤더 포함), `env`(환경값), `query_string`(URL 매개변수)을 제거한다. 두 앱의 `app.py`가 앱 생성 시 이 초기화를 호출하므로 개발 실행과 Waitress 실행에 같은 설정이 적용된다.

**4. 실습 오류 수정 전후.** `5248d81`의 `general/app.py` `create_app()` 안 `sentry_test()`는 `jsonify(result=1 / 0)`에서 `ZeroDivisionError`를 일으킨다. `1becad4`는 그 한 줄을 `jsonify(status="ok", message="실습 오류가 수정되었습니다.")`로 바꿔 정상 JSON을 반환한다. 실제 변경은 `git diff 5248d81 1becad4 -- general/app.py`로 확인할 수 있고 바로 아래에도 제시한다. 함수 위의 `@login_required`와 `ENABLE_SENTRY_TEST` 검사, 게시글 라우트는 그대로 유지된다. `general/tests/test_board.py`는 로그인하지 않은 요청, 스위치가 꺼진 요청, 켜진 뒤의 정상 응답을 검사한다.

```diff
-        return jsonify(result=1 / 0)
+        return jsonify(status="ok", message="실습 오류가 수정되었습니다.")
```

Python **FastAPI + SQLAlchemy 2** 백엔드와 **Next.js App Router + TypeScript** 프론트엔드로 만든 회원가입 프로젝트입니다. 이름, 이메일, 비밀번호, 비밀번호 확인을 입력해 실제 SQLite DB에 회원을 등록합니다. 한국어 반응형 화면, 입력값 검증, 비밀번호 보기, 처리 중 표시, 오류 및 완료 화면을 제공합니다.

## 빠른 실행 (Windows PowerShell)

Node.js 20.9 이상과 Python 3.12 이상을 준비합니다. 프로젝트 폴더에서:

```powershell
.\setup.ps1
.\start.ps1
```

`setup.ps1`은 Python 가상환경, 패키지, Next.js 패키지와 개별 암호화 키를 준비합니다. `start.ps1`은 서버를 실행하고 `http://127.0.0.1:3000`을 엽니다. 서버는 숨겨진 프로세스로 실행되고 로그는 `.run/`에 저장됩니다. 중지:

```powershell
.\stop.ps1
```

PowerShell이 로컬 스크립트 실행을 제한한다면 **이 프로젝트의 스크립트에 한해** 다음처럼 실행할 수 있습니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\start.ps1
```

## 수동 실행 (Windows / macOS / Linux)

백엔드 터미널:

```text
cd backend
python -m venv .venv
```

Windows에서는 `.venv\Scripts\Activate.ps1`, macOS/Linux에서는 `source .venv/bin/activate`로 활성화한 후:

```text
python -m pip install -r requirements-lock.txt
python scripts/setup_env.py
python -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

프론트엔드 터미널:

```text
cd frontend
npm ci
npm run dev
```

- 화면: http://127.0.0.1:3000
- API 문서: http://127.0.0.1:8000/docs
- 상태 확인: http://127.0.0.1:8000/api/health

기본 설정으로 동작하므로 프론트엔드 환경 파일은 필요 없습니다. 백엔드 주소를 변경하려면 `frontend/.env.example`을 `.env.local`로 복사해 `API_BASE_URL`을 수정하고 Next.js를 재시작/재빌드하세요. 브라우저는 같은 출처의 `/api`로 요청하고 Next.js가 Python 서버로 전달합니다.

## 디렉터리 구조

```text
backend/
  app/
    api/routes.py             # HTTP 엔드포인트
    core/config.py            # 환경변수 및 키 검증
    core/security.py          # 암호화, 이메일 검색용 HMAC, 비밀번호 해시
    db/                       # SQLAlchemy Base, 세션 의존성
    models/member.py          # 테이블 모델
    schemas/member.py         # 요청 검증 및 응답 구조
    repositories/members.py   # DB 조회/저장
    services/signup.py        # 회원가입 업무 로직
    main.py                   # 앱 생성, DB 초기화, 오류 응답
  scripts/setup_env.py        # 안전한 개별 키 생성
  tests/test_signup.py        # 통합 테스트
  data/                      # 자동 생성되는 SQLite DB (배포 소스 제외)
frontend/
  src/app/                   # 페이지, 레이아웃, 스타일
  src/components/            # 회원가입 폼과 UI 상태
  src/lib/api.ts             # API 통신 및 오류 처리
  src/types/auth.ts          # 타입 정의
```

## 저장 방식

| 항목 | DB 저장 방식 |
|---|---|
| 이름, 이메일 | Fernet 인증 암호화 |
| 비밀번호 | Argon2id 단방향 해시, 임의 salt |
| 이메일 중복 확인 | 별도 비밀 키의 HMAC-SHA256 + UNIQUE 제약 |
| 식별자, 가입 시각 | UUID, 가입 시간 |

이메일은 앞뒤 공백을 제거하고 소문자로 정규화합니다. 이름은 NFC 정규화 및 앞뒤 공백 제거를 적용합니다. 비밀번호는 공백을 임의로 제거하지 않으며 12~128자 길이와 확인 일치를 검사합니다. API 오류에는 요청 원문/비밀번호를 되돌려 보내지 않습니다. 가입 응답에는 식별자, 시각, 완료 메시지만 포함됩니다.

DB 기본 경로는 `backend/data/members.db`입니다. 재시작해도 데이터가 유지됩니다. `.env`의 두 키는 설치 시 무작위 생성되며 기존 파일이 있으면 덮어쓰지 않습니다. **키를 잃으면 복호화할 수 없으므로 DB와 키를 각각 안전하게 백업해야 합니다.** 두 키를 임의로 교체하면 기존 정보 복호화 및 중복 확인이 실패합니다. `.env`, DB, 가상환경, 빌드 파일은 Git과 제공 ZIP에서 제외됩니다.

## API

`POST /api/auth/signup`

```json
{
  "name": "홍길동",
  "email": "hello@example.com",
  "password": "my long unique passphrase",
  "password_confirmation": "my long unique passphrase"
}
```

성공은 `201`, 중복 이메일은 `409`, 입력값 오류는 `422`입니다. DB의 UNIQUE 제약으로 동시 가입 요청에서도 중복 저장을 방지합니다.

## 검증

```text
cd backend
python -m pip install -r requirements-dev-lock.txt
python -m pytest -q
python -m compileall -q app scripts tests
```

```text
cd frontend
npm run typecheck
npm run build
```

테스트는 임시 DB와 임시 키를 사용합니다. 실제 DB/키는 변경하지 않습니다. 저장된 원문 부재, 복호화, Argon2 검증, 이메일 정규화 및 중복 처리, 동시 요청, 잘못된 입력, 오류의 비밀번호 유출 방지, 재시작 후 영속성을 검사합니다. 정확한 패키지 버전은 Python lock 파일과 `frontend/package-lock.json`에 고정되어 있습니다.

## 요구사항 대응

1. 문법 검증: Python compileall, TypeScript 검사, Next.js 프로덕션 빌드.
2. 회원정보 보호: 이름/이메일 암호화, 비밀번호 Argon2id 해시.
3. DB 저장: SQLite 영구 저장.
4. 백엔드 언어: Python.
5. DB ORM: SQLAlchemy 2.
6. 프론트엔드: Next.js.
7. 모듈 분리: 프론트/백엔드 및 각 책임별 디렉터리 분리.

범위는 로컬 회원가입 구현입니다. 로그인, 이메일 인증, 비밀번호 재설정은 포함하지 않습니다. 공개 서비스로 운영할 때는 HTTPS, 요청 제한, 실제 개인정보 처리정책, 백업 및 키 관리, 스키마 변경을 위한 마이그레이션을 추가해야 합니다. 현재 테이블은 최초 실행 시 `create_all`로 생성합니다.

구현 참고: [Next.js 공식 문서](https://nextjs.org/docs/app/getting-started/installation), [FastAPI 비밀번호 해시](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [SQLAlchemy 선언형 모델](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html), [Fernet](https://cryptography.io/en/latest/fernet/).


## React 감시 대시보드 (Day 04)

Flask/PostgreSQL 게시판과 React/Vite 감시 대시보드의 실행 및 DB 준비 방법은 [monitor/README.md](monitor/README.md)를 참고하세요. 기존 회원가입 서비스는 유지됩니다.

## Docker 일반·감시 미니프로젝트 (Day 1)

이 저장소의 **직접 만든** `general` Flask 게시판, `monitor/backend` Flask 감시 API, `monitor/next-frontend` Next.js 화면을 사용한다. 수업의 `mini-watch-day06`을 복사하지 않았으므로 폴더 이름만 다르고 역할은 같다. 이번 작업에서 두 Compose, 세 Dockerfile과 `.dockerignore`, 두 Nginx gateway, 일반 로그인·기록 종류, 감시 기록 화면, Docker 통합 검증을 완성했다. DB 초기 SQL은 새 사본 대신 기존 `general/sql/posts.sql`과 `monitor/backend/sql/schema.sql`을 컨테이너의 `/docker-entrypoint-initdb.d/01-schema.sql`에 연결한다.

### 처음 실행 (저장소 루트, Windows PowerShell)

Docker 엔진이 실행 중이어야 한다. 두 Compose는 합쳐 실행하지 않는다. `.env.example`의 값은 실습 전용이며, 실제 운영용 비밀번호·세션 키를 넣지 않는다. 필요하면 루트에 `.env`를 복사해 값을 바꾼다. **이미 생성된 DB 볼륨의 비밀번호는 `.env` 변경만으로 바뀌지 않는다.**

```powershell
Copy-Item .env.example .env
docker network create m5d1-events
docker compose -f compose-general.yaml config --quiet
docker compose -f compose-monitor.yaml config --quiet
docker compose -f compose-monitor.yaml up -d --build
docker compose -f compose-monitor.yaml ps
docker compose -f compose-monitor.yaml logs --tail=30 monitor-api monitor-web
curl.exe http://localhost:8082/api/health
docker compose -f compose-monitor.yaml exec monitor-api python create_user.py
```

마지막 명령에 실습용 `operator`, 표시 이름 `운영자`, 비밀번호 `Learn123!`를 입력한다. `http://localhost:8082`에서 로그인한 뒤 같은 브라우저에서 `http://localhost:8082/api/auth/me`를 열어 HTTP 200과 운영자 정보를 확인한다. 로그인 전 이 보호 API는 401이다. **감시 API가 준비된 뒤** 일반 프로젝트를 시작한다.

```powershell
docker compose -f compose-general.yaml up -d --build
docker compose -f compose-general.yaml ps
docker compose -f compose-general.yaml logs --tail=30 general-api
docker compose -f compose-general.yaml exec general-api python create_user.py
docker network inspect m5d1-events
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
```

일반 계정은 `student` / `Learn123!`로 만든다. 공개 주소는 일반 `http://localhost:8081`, 감시 `http://localhost:8082`다. 일반 로그인 화면에서 잘못된 비밀번호와 올바른 비밀번호를 차례로 입력하고 게시글 화면을 연다. 감시 화면에서 `기록 불러오기`를 누르면 `login_failure`·401과 `login_success`·200을 확인할 수 있다. 성공한 로그인은 실제 HTTP 응답에서 게시글 목록으로 303 이동하며, 감시 기록의 **로그인 결과 코드**는 200으로 저장한다. 감시 메모에 제목 `Docker 점검`, 내용 `로그인 실패와 성공을 확인했다`를 등록한 뒤 새로고침해 다시 조회한다.

| 네트워크 | 참여 서비스 | 공개 포트 |
| --- | --- | --- |
| `general-front` | `general-gateway`, `general-api` | gateway의 8081만 |
| `general-data-net` | `general-api`, `general-db` | 없음 |
| `monitor-front` | `monitor-gateway`, `monitor-web`, `monitor-api` | gateway의 8082만 |
| `monitor-data-net` | `monitor-api`, `monitor-db` | 없음 |
| 외부 `m5d1-events` | `general-api`, `monitor-api` | 없음 |

두 Compose의 프로젝트 이름은 `m5d1-general`, `m5d1-monitor`이고 DB 볼륨도 각각 `general-data`, `monitor-data`다. `general-api`는 `general-db:5432/general_db`, `monitor-api`는 `monitor-db:5432/monitor_db`에 접속한다. 기록 전송 주소는 `http://monitor-api:5000/api/events`다. 동일한 네트워크 **별칭만** 각 Compose에 적으면 서로 다른 격리된 망이 생겨 이름 조회가 되지 않는다. 두 파일에서 `external: true`와 실제 이름 `m5d1-events`를 같이 지정하고 두 API를 참여시켜야 한다. DB는 그 공유 망에 없다. 로컬 PC의 공개 포트나 `localhost`는 컨테이너 사이의 상대 서비스 주소가 아니다.

`config --quiet`는 Compose 설정을 파싱하고, `ps`는 컨테이너 상태·DB healthcheck와 gateway 공개 포트를 본다. `logs`는 Flask·Next 시작 또는 오류를 확인한다. `network inspect`는 공유 망의 두 API 참여를 확인한다. API 안의 `getent hosts monitor-api`는 이름이 IP로 해석되는지만 확인한다. **실제 기록 전달은** 일반 로그인 후 감시 `/api/events`의 결과로 따로 확인한다.

감시 `monitor-web`에도 HTTP healthcheck를 두고 `monitor-gateway`가 화면 준비를 기다리게 했다. 이 작은 설정 개선은 Next.js 빌드 이미지가 실행을 시작했지만 아직 요청을 받지 못하는 순간의 gateway 시작 순서를 명확히 한다.

자료 보존을 확인하려면 두 프로젝트를 별도로 내려 다시 올린다. `down`에 `-v`를 붙이지 않는다. DB의 실제 데이터 경로 `/var/lib/postgresql/data`에 각각 named volume이 연결되어 있어 컨테이너를 새로 만들어도 기록·메모·계정이 남는다.

```powershell
docker compose -f compose-general.yaml down
docker compose -f compose-monitor.yaml down
docker compose -f compose-monitor.yaml up -d
docker compose -f compose-general.yaml up -d
```

### 심화: 망 분리·복구, 변경 반영, DB 분리

공유 망의 영향을 실험하려면 일반 API 컨테이너 ID를 얻어 **그 컨테이너만** 분리한다. 이 동안 `getent`는 `monitor-api`를 찾지 못하고 새 로그인 기록도 전송되지 않는다. 전송 실패분을 다시 보내는 큐는 없으므로 복구 후 새 실패·성공 로그인을 만든다. 마지막 명령으로 원래 공유 망 참여를 복구한다.

```powershell
$generalApi = (docker compose -f compose-general.yaml ps -q general-api)
docker network disconnect m5d1-events $generalApi
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
docker network connect --alias general-api m5d1-events $generalApi
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
```

Flask Dockerfile은 `COPY . .`로 소스를 이미지에 넣고, Compose의 볼륨은 **DB 데이터만** 연결한다. 따라서 Flask 소스를 고친 뒤 `docker compose -f compose-general.yaml restart general-api`는 이전 이미지·코드를 다시 시작할 뿐이다. 변경을 반영하려면 아래처럼 빌드 후 컨테이너를 재생성한다. 감시 API도 같은 방식이며, Next.js 소스는 이미지 빌드 중 `npm run build`를 다시 해야 한다.

```powershell
docker compose -f compose-general.yaml up -d --build --force-recreate general-api general-gateway
docker compose -f compose-monitor.yaml up -d --build --force-recreate monitor-api monitor-web monitor-gateway
```

일반 API 안의 `getent hosts general-db`는 자기 DB IP를 찾고, `getent hosts monitor-db`는 다른 DB가 일반 DB 망이나 공유 망에 없으므로 실패한다. 이름 조회 성공은 DNS 연결만 뜻한다. 실제 DB 접속은 별도의 계정·비밀번호 인증이 필요하고, SQL 실행 성공은 그 뒤의 스키마·권한까지 확인한다.

```powershell
docker compose -f compose-general.yaml exec general-api getent hosts general-db
docker compose -f compose-general.yaml exec general-api getent hosts monitor-db
```

Docker 적용의 핵심 커밋은 `0ce056a` (`Containerize general and monitor services with shared event network`)다. 두 Compose, Dockerfile·ignore, gateway, 일반 로그인·감시 기록 화면, SQL과 통합 검증을 추가했다. 별도 작업 브랜치 `feature/monitor-web-health`의 개선 커밋 `bf6bd41`은 Next.js healthcheck와 gateway 대기 조건을 `compose-monitor.yaml`에 추가하고 `README.md`, `monitor/README.md`의 안내를 보완했다. [PR #15](https://github.com/cjw25/moa-signup/pull/15)의 Files changed에서 세 파일을 확인했고 `docker compose -f compose-monitor.yaml config --quiet`가 통과했다. 병합 상태와 실제 Docker CI 결과도 해당 PR에서 확인할 수 있다. Docker 통합 검증은 `.github/workflows/docker.yml`과 `tests/docker_integration.py`가 같은 순서로 두 Compose를 실제 실행하고, 공유 DNS·로그인 기록·메모와 `down` 뒤 DB 보존을 확인한다.
