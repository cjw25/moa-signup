from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.api.routes import router
from app.core.config import BACKEND_DIR, Settings
from app.core.security import MemberSecurity
from app.db.base import Base
from app.services.signup import EmailAlreadyRegistered


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    url = make_url(config.database_url)
    connect_args = {"check_same_thread": False, "timeout": 10} if url.get_backend_name() == "sqlite" else {}
    engine = create_engine(config.database_url, connect_args=connect_args, hide_parameters=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        (BACKEND_DIR / "data").mkdir(exist_ok=True)
        Base.metadata.create_all(engine)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="모아 회원가입 API", version="1.0.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    app.state.security = MemberSecurity(config)
    app.include_router(router)

    @app.middleware("http")
    async def private_response_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(EmailAlreadyRegistered)
    async def duplicate_email(request: Request, exc: EmailAlreadyRegistered):
        return JSONResponse(status_code=409, content={
            "message": "이미 가입된 이메일입니다. 다른 이메일을 입력해 주세요.",
            "errors": {"email": "이미 가입된 이메일입니다."},
        })

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError):
        # Never return Pydantic's `input` field: it may contain a plaintext password.
        field_messages = {
            "name": "이름은 2~50자로 입력해 주세요. 제어 문자는 사용할 수 없습니다.",
            "email": "올바른 이메일 주소를 입력해 주세요.",
            "password": "비밀번호는 공백만 사용하지 않고 12~128자로 입력해 주세요.",
            "password_confirmation": "비밀번호 확인을 동일하게 입력해 주세요.",
        }
        errors = {}
        for error in exc.errors():
            field = str(error["loc"][-1])
            if field in field_messages:
                errors[field] = field_messages[field]
        return JSONResponse(status_code=422, content={
            "message": "입력 내용을 확인해 주세요.", "errors": errors,
        })

    return app
