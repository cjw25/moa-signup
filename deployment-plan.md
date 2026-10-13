# Day2 일반·감시 배포 계획

## 출발점과 상태

- 저장소: `cjw25/moa-signup`, 작업 및 제출 브랜치: `day2-deploy`.
- 시작 코드: 이 저장소의 Day1 일반 Flask 게시판, 감시 Flask API, 감시 Next.js 화면, 두 Compose 및 gateway. 기존 회원가입 FastAPI/Next 앱도 저장소에 남아 있다.
- Render, Supabase, Sentry 계정과 실제 서비스 주소가 제공되지 않아 세 앱 모두 **미배포**. 외부 DB의 데이터 조회와 Sentry 수신도 확인하지 않았다. 이 문서는 배포 가능한 소스와 설정 절차를 기록한다.
- 수업 범위: Render Hobby/Free Docker Web Service, Supabase Free 프로젝트 두 개, Sentry Developer. 유료 전환은 필요하지 않다.

| 앱 | Root Directory | Dockerfile Path | Docker Build Context | Health Check Path | 상태 |
|---|---|---|---|---|---|
| 감시 API | `monitor/backend` | `./Dockerfile` | `.` | `/health` | 미배포 |
| 일반 앱 | `general` | `./Dockerfile` | `.` | `/health` | 미배포 |
| 감시 화면 | `monitor/next-frontend` | `./Dockerfile` | `.` | `/` | 미배포 |

세 Web Service 모두 GitHub 저장소의 `day2-deploy` 브랜치, Docker 환경, **Docker Command 빈칸**, Auto-Deploy **On Commit**으로 설정한다. 각 Dockerfile이 시작 명령을 제공한다. Flask Dockerfile은 Waitress의 `app:app`을 `0.0.0.0:$PORT`로 실행한다. `python app.py`는 개발 실행이다. Next Dockerfile은 `npm ci` → `npm run build` → `npm run start` 순서이며 빌드에는 API/DB 연결이 필요하지 않다. `compose-general.yaml`, `compose-monitor.yaml`, `gateways/`는 로컬 두 프로젝트용이고 Render는 앱별 Dockerfile로 실행한다.

## DB와 환경 변수

일반 Supabase 프로젝트의 Session pooler **Host/User**를 `general/.env.example`의 `DB_HOST`/`DB_USER`에, 별도 감시 Supabase 프로젝트의 Host/User를 `monitor/backend/.env.example`에 대응시킨다. 두 프로젝트 모두 포트 `5432`, DB 이름 `postgres`, `DB_SSLMODE=require`를 쓴다. 두 DB의 이름이 같아도 서로 다른 프로젝트다. 수업용 프로젝트의 Data API를 끄고 Flask가 PostgreSQL에 직접 연결한다. RLS 정책은 이 과제 범위에 추가하지 않는다. 실제 `DB_PASSWORD`는 각 서비스 환경 변수에만 둔다. 로컬 Compose PostgreSQL은 SSL 없이 각각 다른 DB/볼륨을 사용한다. 기존 `DATABASE_URL` 방식은 CI 호환을 위한 대체 경로이며 `DB_HOST`가 있으면 분리된 DB 변수를 우선한다.

일반 프로젝트에서는 `general/sql/deploy.sql`을, 감시 프로젝트에서는 `monitor/backend/sql/deploy.sql`을 실행한다. 실제 코드가 사용하는 이름은 일반 `general_users`(users), `posts`, 감시 `monitor_users`(users), `request_events`(http_events), `observation_notes`(notes)다. 배포 SQL은 `CREATE TABLE IF NOT EXISTS`와 누락 열의 `ADD COLUMN IF NOT EXISTS`만 사용하며 기존 자료를 삭제하지 않는다. 두 Flask 폴더별 로컬 가상환경에서 의존성을 설치하고 해당 DB 환경 변수로 `python create_user.py`를 실행해 비밀번호 해시를 저장한다. 각 앱은 자신의 DB에서 게시글/메모 CRUD를 수행하므로 앱 재시작과 재배포 후에도 같은 외부 DB를 다시 읽는다.

| 환경 변수 | 설정 위치와 역할 |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE` | 각 Flask의 별도 DB 연결 |
| `SECRET_KEY`, `SESSION_COOKIE_SECURE` | 각 Flask의 서로 다른 세션 키; 로컬 HTTP는 `false`, Render HTTPS는 `true` |
| `MONITOR_URL` | 일반 Flask 서버의 감시 Flask HTTPS 주소 + `/api/events` |
| `EVENT_TOKEN` | 일반/감시 Flask 서버에 같은 비밀값; `X-Event-Token`으로 기록 수신 검증 |
| `MONITOR_API_URL` | Next 서버의 감시 Flask HTTPS 기준 주소, `/api` 접미사 없이 설정 |
| `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `APP_VERSION` | 각 Flask의 Sentry 설정과 릴리스 식별자 |
| `ENABLE_SENTRY_TEST` | 일반 Flask 실습 경로 스위치; 기본 `false` |

비밀번호·키·토큰·DSN은 예시 파일이나 브라우저의 `NEXT_PUBLIC_*`에 넣지 않는다. `SENTRY_DSN`이 비어 있으면 SDK 전송을 시작하지 않는다. 감시 화면은 `MONITOR_API_URL`만 서버에서 읽는다.

## 요청 흐름과 확인

브라우저 → 감시 Next의 동일 출처 `/api/...` → `app/api/[...path]/route.js` → 감시 Flask → 감시 DB. Next 프록시는 요청의 `Cookie`, `X-CSRF-Token` 및 응답의 `Set-Cookie`, 상태 코드를 전달한다. 일반 브라우저 → 일반 Flask → 일반 DB이며, 일반 Flask는 요청 메타데이터를 `MONITOR_URL`로 전송한다. 감시 Flask는 토큰을 확인하고 `login_failure`/401, `login_success`/200 등을 분류·저장한다. 비밀번호와 토큰은 브라우저에 전달되지 않는다.

1. 감시 Flask `/health`, 일반 Flask `/health`, Next `/`의 응답을 확인한다. `/health`는 앱 프로세스 확인용이며 DB 연결·로그인 성공을 보장하지 않는다.
2. 감시 화면의 `/api/auth/me` 확인 후 운영자 계정으로 로그인한다. 일반 앱에서 로그인 실패/성공을 만든 뒤 감시 기록의 401/200과 종류를 확인한다.
3. 일반 게시글과 감시 메모를 등록·수정·새로고침하고 해당 DB 행을 조회한다. 재배포 뒤에도 같은 DB 행이 표시되는지 확인한다.
4. 일반 앱의 `ENABLE_SENTRY_TEST=true`를 잠시 설정하고 로그인 후 `/api/sentry-test`를 확인한다. 현재 수정 코드에서는 정상 JSON을 반환한다. 오류 재현은 이전 커밋 `5248d81`에서만 가능하다. 확인 후 `false`로 복원한다. 실제 Sentry 수신은 아직 검증되지 않았다.
5. 코드 수정 → 커밋 → push → Render가 선택한 배포 커밋 확인 → 같은 기능 재확인 순으로 진행한다. Sentry의 Resolve 조작은 코드 수정이나 재배포를 대신하지 않는다.

## 문제 진단과 실패 안내

| 증상 | 코드에서 응답한 곳 | 먼저 확인할 곳 |
|---|---|---|
| 감시 화면 `/api/...`가 `503`와 `감시 API 주소가 설정되지 않았습니다.` | Next `app/api/[...path]/route.js`의 `MONITOR_API_URL` 누락 분기 | 감시 Next 서비스의 `MONITOR_API_URL` 서버 환경 변수 |
| 감시 화면 `/api/...`가 `502`와 `감시 API에 연결하지 못했습니다. 잠시 후 다시 불러와 주세요.` | 같은 Route Handler의 `fetch` 연결 예외 처리 | Next 서비스 로그, 감시 Flask의 HTTPS 기준 주소와 실행 상태 |
| 일반 앱은 동작하지만 감시 기록이 없음 | `general/request_logging.py`의 전송 경고 또는 감시 `routes/events.py`의 토큰 `403` | 일반 Flask 로그, `MONITOR_URL`의 `/api/events`, 양쪽 `EVENT_TOKEN` |
| 로그인·게시글·메모 조회나 저장이 실패 | 각 Flask의 `db.py`와 repositories가 PostgreSQL에 연결·질의 | **실패한 Flask** 로그의 DB 예외, 해당 Supabase 프로젝트의 Session pooler Host/User, 암호와 SSL 설정 |
| 로그인 입력 오류 `400`/`401`, 기록 필터 오류 `400`, 메모 본문·상태 오류 `400`, 일반 게시글 입력 오류 `400` | 감시 `routes/auth.py`, `routes/events.py`, `routes/notes.py`; 일반 `routes/posts.py` | API 응답 `message` 또는 일반 화면 오류 문구와 입력값 |

Next 프록시는 감시 Flask가 응답한 상태 코드(예: `400`, `401`, DB 예외의 `500`)를 그대로 전달한다. 연결 자체가 안 될 때의 `502`와 구별한다. `lib/api.js`는 JSON `message`와 HTTP `status`를 Error에 담고, `components/MemoDashboard.js`의 `report()` 및 첫 `getMe()` 실패 처리에서 `role="alert"` 오류 문구를 띄운다. 로그인 화면은 **로그인**을 다시 눌러 요청하고, 로그인 후에는 `components/EventList.js`의 **기록 불러오기** 또는 메모 목록의 **새로고침** 버튼이 `refreshEvents()`/`refresh()`를 다시 실행한다. 이 함수들은 시작할 때 이전 오류를 지운다.

두 Flask의 `/health`는 `app.py`에서 DB 쿼리를 실행하지 않고 `{"status":"ok"}`를 반환한다. 따라서 `200`은 프로세스 상태만 뜻하며 DB 연결·로그인·쓰기 성공의 증거가 아니다. 실제 계정 로그인과 게시글/메모 CRUD 및 DB 행 조회를 별도로 확인한다.

## Sentry와 오류 수정 이력

`general/observability.py`, `monitor/backend/observability.py`는 각 `app.py`의 `create_app()`에서 초기화된다. `send_default_pii=False`는 기본 사용자 정보 수집을 끄고 `max_request_body_size="never"`는 요청 본문 자동 수집을 막는다. `before_send=remove_private_data`는 전송 직전에 최상위 `user`와 요청의 `data`(본문), `cookies`(세션 쿠키), `headers`(인증 헤더 포함), `env`(환경값), `query_string`(URL 매개변수)을 삭제한다. 따라서 개발 실행과 Waitress 실행에 같은 제외 규칙이 적용된다. 두 서비스는 `mini-general`, `mini-monitor` 태그로 구분한다.

| 커밋 | 변경 | 의미 |
|---|---|---|
| `5248d81` | `general/app.py`의 `sentry_test()`에 `1 / 0` 포함; 배포·DB·프록시·Sentry 코드 추가 | 로그인과 스위치가 켜진 경우 실습 오류 재현 상태 |
| `1becad4` | `general/app.py`, `general/tests/test_board.py` | 0으로 나누는 식을 정상 JSON으로 교체하고 로그인/스위치 검사 추가 |
| `65a7ec3` | `deployment-plan.md`, `README.md`, 감시 API 테스트 | 배포 설정과 오류 수정 이력 문서화 |
| `6956ba4` | `monitor/next-frontend/app/api/[...path]/route.js` | 본문 없는 204 응답을 Next 프록시가 그대로 전달하도록 수정 |

오류 수정 diff (`git diff 5248d81 1becad4 -- general/app.py`):

```diff
-        return jsonify(result=1 / 0)
+        return jsonify(status="ok", message="실습 오류가 수정되었습니다.")
```

이 변경은 `sentry_test()`의 응답식만 고쳤다. 로그인 검사와 `ENABLE_SENTRY_TEST` 조건, 게시글 라우트는 유지된다.
