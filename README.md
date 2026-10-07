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
