# Flask 게시판

게시글 CRUD와 요청 기록 전송 기능을 제공합니다. 게시판과 감시 API는 같은 PostgreSQL DB를 사용합니다. DB 준비와 세 서비스 실행 순서는 [감시 대시보드 README](../monitor/README.md)에 있습니다.

기본 주소는 http://127.0.0.1:5100 입니다. `general/.env`의 `DATABASE_URL`은 PostgreSQL 접속 정보이고, `MONITOR_URL`은 감시 API의 `http://127.0.0.1:5200/events`입니다. 게시판 요청 뒤 감시 화면에서 목록 새로고침을 누르면 요청 기록을 확인할 수 있습니다.
