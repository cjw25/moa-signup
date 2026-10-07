# React 감시 대시보드

기존 `general` 게시판을 유지하고 Flask 감시 API와 React/Vite 화면을 추가했습니다. 요청 기록과 관찰 메모, 운영자 계정은 PostgreSQL에 저장합니다. Flask의 서명된 쿠키 세션으로 로그인 상태를 유지하며, 새로고침 후에도 대시보드로 돌아옵니다. 요청 기록 조회와 메모 API는 로그인 여부를 검사합니다. 일반 서비스의 기록 수신 주소 `/events`는 서버 간 전송을 위해 별도로 열어 둡니다.

## 준비와 실행 (Windows CMD)

Python 3.12 이상, Node.js 20.9 이상, PostgreSQL을 설치합니다. 저장소 루트에서 DB를 만들고 테이블을 준비합니다. 이미 만든 DB가 있다면 생성 단계는 건너뜁니다.

```cmd
psql -U postgres -c "CREATE DATABASE mini_watch;"
psql -U postgres -d mini_watch -f general\sql\posts.sql
psql -U postgres -d mini_watch -f monitor\backend\sql\schema.sql
```

서로 다른 CMD 창 세 개에서 실행합니다. 두 `.env` 파일의 `DATABASE_URL`에 실제 PostgreSQL 비밀번호를 입력합니다. 두 서비스가 같은 DB를 바라봐야 합니다. `MONITOR_URL`은 게시판의 요청 기록 수신 주소입니다. 감시 서비스의 `MONITOR_SECRET_KEY`는 세션 쿠키 서명용이며, 아래 준비 명령이 무작위 값으로 생성합니다. 기존 키를 바꾸면 기존 로그인 세션은 무효화됩니다.

```cmd
cd general
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python app.py
```

```cmd
cd monitor\backend
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python -m scripts.setup_env
.venv\Scripts\python -m scripts.create_admin
.venv\Scripts\python app.py
```

```cmd
cd monitor\frontend
npm ci
npm run dev
```

주소: 게시판 http://127.0.0.1:5100, 감시 API http://127.0.0.1:5200, 감시 화면 http://127.0.0.1:5173. 운영자 계정 생성 명령은 아이디·표시 이름·비밀번호를 대화형으로 받으며 해시만 DB에 저장합니다. 실제 비밀번호는 Git에 넣지 않습니다.

## 기능과 확인

게시판의 상세·없는 글 요청을 발생시킨 뒤 감시 화면에서 로그인합니다. 틀린 비밀번호는 401 안내, 빈 입력은 400 안내가 나옵니다. 대시보드의 목록 새로고침으로 요청 경로와 상태 코드를 확인합니다. 경로나 상태 코드로 검색하고 조건을 해제하면 전체 기록이 다시 표시됩니다. 화면의 전체·오류 건수는 현재 조회 결과를 기준으로 하며 오류는 HTTP 400 이상입니다. 메모 작성·상세·수정·삭제 확인과 취소를 사용한 뒤 다시 조회합니다. 메모의 처리 상태는 확인 전·확인 중·완료 중 선택하며 DB에 저장합니다. 공백 입력은 400, 없는 메모는 404입니다. 화면을 새로고침해도 로그인과 DB 자료가 유지되고, 로그아웃하면 보호 API는 401을 반환합니다.

구현된 필수 기능: 로그인 판정과 화면 전환, 요청 기록 수집·조회, 메모 CRUD, 오류 처리, React 컴포넌트·API 분리, Flask 라우트·저장소 분리. 선택 심화 기능 네 가지도 구현했습니다: 요청 기록 검색·필터, 조회 건수 요약, 메모 처리 상태, 쿠키 세션과 API 보호.

검증 명령:

```cmd
cd monitor\backend
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest -q
cd ..\frontend
npm ci
npm run build
```

과제의 시작 자료는 이전 작업에서 만든 `general` 게시판과 요청 전송 코드입니다. 이번 작업에서는 감시 기록을 메모리 저장에서 PostgreSQL 저장으로 바꾸고, 운영자 로그인·메모 API·React 화면과 심화 기능을 구현했습니다. 기존 DB에 `observation_notes` 테이블이 있으면 `sql/schema.sql`을 다시 실행하여 `status` 열을 추가합니다. GitHub Actions의 PostgreSQL 통합 테스트에서 게시판 요청 기록, 로그인·세션·API 보호, 메모 CRUD와 처리 상태, DB 저장, 검색·필터, Vite 프록시 연결을 확인합니다. 브라우저의 실제 화면 조작은 위 시나리오에 따라 확인할 수 있습니다.
