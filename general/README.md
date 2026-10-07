# Flask 게시판

기존 회원가입 서비스와 독립적으로 실행하는 게시판입니다. Flask, Jinja2, PostgreSQL을 사용합니다.

## 준비

PostgreSQL 데이터베이스를 만들고 `sql/posts.sql`을 실행합니다. 기존 `posts` 테이블이 있으면 스키마를 확인한 뒤 SQL 적용 여부를 결정하세요.

```powershell
cd general
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`의 `DATABASE_URL`을 실제 접속 정보로 수정한 뒤 `python app.py`를 실행합니다. 기본 주소는 http://127.0.0.1:5000 입니다.

감시 서버는 저장소 루트에서 별도 터미널로 실행할 수 있습니다.

```powershell
cd monitor/backend
pip install -r requirements.txt
python app.py
```

`MONITOR_URL`이 설정되면 게시판 요청 기록을 JSON으로 전송합니다. 수집 결과는 http://127.0.0.1:5001/events 에서 확인합니다.
