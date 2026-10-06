from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import MemberSecurity
from app.models.member import Member
from app.repositories.members import find_by_email_index, save_member
from app.schemas.member import SignupRequest


class EmailAlreadyRegistered(Exception):
    pass


def register_member(session: Session, security: MemberSecurity, data: SignupRequest) -> Member:
    email_index = security.email_index(str(data.email))
    if find_by_email_index(session, email_index):
        raise EmailAlreadyRegistered

    member = Member(
        name_encrypted=security.encrypt(data.name),
        email_encrypted=security.encrypt(str(data.email)),
        email_lookup=email_index,
        password_hash=security.hash_password(data.password.get_secret_value()),
    )
    try:
        return save_member(session, member)
    except IntegrityError:
        # The unique DB constraint also prevents concurrent duplicate signups.
        session.rollback()
        if find_by_email_index(session, email_index):
            raise EmailAlreadyRegistered from None
        raise
