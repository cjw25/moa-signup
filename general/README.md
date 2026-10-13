# Flask 일반 게시판

세션 로그인 후 게시글 목록·상세·등록·수정·삭제를 사용합니다. `general_users`와 `posts`는 PostgreSQL에 저장됩니다. 비밀번호는 Werkzeug 해시로 저장하고 원문은 저장하지 않습니다. 로그인 실패·성공 등 요청 기록은 `MONITOR_URL`로 감시 API에 보냅니다.

두 프로젝트를 Docker로 실행하는 권장 절차는 [루트 README](../README.md#docker-일반감시-미니프로젝트-day-1)에 있습니다. 이 서비스는 `compose-general.yaml`의 `general-db`, `general-api`, `general-gateway`가 담당하고 PC에서는 `http://localhost:8081`로 접속합니다. 일반 API는 `general-db:5432`와 공유 망의 `monitor-api:5000`을 사용합니다.

로컬에서 직접 실행할 때는 `sql/posts.sql`을 PostgreSQL에 적용하고 `.env.example`의 `DATABASE_URL`, `MONITOR_URL`을 실제 로컬 주소에 맞춥니다. `GENERAL_SECRET_KEY`도 설정합니다. `python create_user.py`로 계정을 만든 뒤 `python app.py`로 시작합니다. 로컬 기본 주소는 `http://127.0.0.1:5100`입니다.
