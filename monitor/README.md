# React 감시 대시보드

기존 `general` 게시판을 유지하고 Flask 감시 API와 React/Vite 화면을 추가했습니다. 요청 기록과 관찰 메모, 운영자 계정은 PostgreSQL에 저장합니다. 로그인 상태는 React 메모리에만 유지되므로 새로고침하면 로그인 화면으로 돌아갑니다. API 접근 제한과 세션 유지는 이번 필수 범위에 포함하지 않았습니다.

## 준비와 실행 (Windows CMD)

Python 3.12 이상, Node.js 20.9 이상, PostgreSQL을 설치합니다. 저장소 루트에서 DB를 만들고 테이블을 준비합니다. 이미 만든 DB가 있다면 생성 단계는 건너뜁니다.

```cmd
psql -U postgres -c "CREATE DATABASE mini_watch;"
psql -U postgres -d mini_watch -f general\sql\posts.sql
psql -U postgres -d mini_watch -f monitor\backend\sql\schema.sql
```

서로 다른 CMD 창 세 개에서 실행합니다. 두 `.env` 파일의 `DATABASE_URL`에 실제 PostgreSQL 비밀번호를 입력합니다. 두 서비스가 같은 DB를 바라봐야 합니다. `MONITOR_URL`은 게시판의 요청 기록 수신 주소입니다.

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

게시판의 상세·없는 글 요청을 발생시킨 뒤 감시 화면에서 로그인합니다. 틀린 비밀번호는 401 안내, 빈 입력은 400 안내가 나옵니다. 대시보드의 목록 새로고침으로 요청 경로와 상태 코드를 확인합니다. 메모 작성·상세·수정·삭제 확인과 취소를 사용한 뒤 다시 조회합니다. 공백 입력은 400, 없는 메모는 404입니다. 화면을 새로고침해 재로그인해도 메모와 요청 기록은 DB에 남습니다.

구현된 필수 기능: 로그인 판정과 화면 전환, 요청 기록 수집·조회, 메모 CRUD, 오류 처리, React 컴포넌트·API 분리, Flask 라우트·저장소 분리. 선택 심화 기능은 추가하지 않았습니다.

검증 명령:

```cmd
cd monitor\backend
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest -q
cd ..\frontend
npm ci
npm run build
```

과제의 시작 자료는 이전 작업에서 만든 `general` 게시판과 요청 전송 코드입니다. 이번 작업에서는 감시 기록을 메모리 저장에서 PostgreSQL 저장으로 바꾸고, 운영자 로그인·메모 API·React 화면을 구현했습니다. 실제 DB를 사용한 통합 확인은 로컬 PostgreSQL을 준비한 뒤 위 시나리오로 수행해야 합니다.
