from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.member import SignupRequest, SignupResponse
from app.services.signup import register_member

router = APIRouter(prefix="/api")


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/signup", response_model=SignupResponse, status_code=201, tags=["auth"])
def signup(
    payload: SignupRequest,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> SignupResponse:
    member = register_member(session, request.app.state.security, payload)
    return SignupResponse(id=member.id, created_at=member.created_at)
