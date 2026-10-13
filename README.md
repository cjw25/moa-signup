# 모아 · 회원가입 프로젝트

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
