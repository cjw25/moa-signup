# Next.js 관찰 메모

기존 `monitor/backend` Flask API와 PostgreSQL을 사용하는 별도 Next.js 화면입니다. JavaScript App Router 프로젝트를 `create-next-app`으로 만든 뒤 `app/page.js`, `app/layout.js`, `components/MemoDashboard.js`, `lib/api.js`, 스타일과 프록시 설정을 구현했습니다. UI는 `use client`와 React state로 입력 상태를 관리하고, 실제 메모는 Flask API를 통해 DB에 저장합니다.

## 준비

Node.js 20.9 이상, Python 3.12 이상, PostgreSQL을 준비합니다. 저장소 루트에서 아래 SQL을 실행합니다. 기존 DB가 있다면 `CREATE DATABASE` 단계는 생략합니다.

```cmd
psql -U postgres -c "CREATE DATABASE mini_watch;"
psql -U postgres -d mini_watch -f monitor\backend\sql\schema.sql
```

`monitor/backend/.env.example`을 `.env`로 복사하고 실제 `DATABASE_URL`을 설정합니다. `MONITOR_SECRET_KEY`는 `scripts.setup_env`로 생성하고 운영자 계정은 `scripts.create_admin`으로 만듭니다. 실제 `.env`와 비밀번호는 커밋하지 않습니다.

```cmd
cd monitor\backend
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python -m scripts.setup_env
.venv\Scripts\python -m scripts.create_admin
.venv\Scripts\python app.py
```

다른 터미널에서 Next.js를 실행합니다. 기본 API 주소는 `http://127.0.0.1:5200`입니다. 다른 주소를 쓸 때는 `.env.example`을 `.env.local`로 복사하고 `MONITOR_API_URL`을 바꿉니다.

```cmd
cd monitor\next-frontend
npm ci
npm run dev -- --port 3002
```

브라우저에서 `http://127.0.0.1:3002`를 엽니다. 운영자 로그인 후 메모 목록에서 항목을 선택하면 상세 GET 요청이 실행됩니다. 새 메모 등록, 수정, 삭제 확인 및 취소가 가능합니다. 빈 제목·내용은 화면에서 거절하며 API의 400·404 등 실패 응답도 오류로 표시합니다. 삭제나 수정을 취소하면 원본이 유지됩니다. 새로고침하면 쿠키 세션을 확인하고 DB 목록을 다시 불러오므로 저장한 메모가 유지됩니다.

요청 기록 영역은 일반 게시판에서 전송한 `login_failure`·`login_success`와 상태 코드를 보여 줍니다. Docker로 실행할 때는 별도의 로컬 개발 서버가 필요 없으며 [루트 Docker 실행 절차](../../README.md#docker-일반감시-미니프로젝트-day-1)를 사용합니다.

## 검증

`npm run build`가 성공했습니다. `npm run start -- --port 3002`로 빌드한 화면을 확인할 수 있습니다. 저장소의 GitHub Actions `integration.yml`은 PostgreSQL 서비스에 Flask와 Next.js를 띄워 로그인 세션, 목록·상세·등록·수정·삭제, 공백 입력 400, 없는 메모 404, 새 요청에서 DB 자료 유지와 DB 행의 내용을 확인합니다. 선택 심화 3·4에 해당합니다.
