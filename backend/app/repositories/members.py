from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member


def find_by_email_index(session: Session, email_index: str) -> Member | None:
    return session.scalar(select(Member).where(Member.email_lookup == email_index))


def save_member(session: Session, member: Member) -> Member:
    session.add(member)
    session.commit()
    session.refresh(member)
    return member
