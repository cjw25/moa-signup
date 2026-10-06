import hashlib
import hmac

from cryptography.fernet import Fernet
from pwdlib import PasswordHash

from app.core.config import Settings


class MemberSecurity:
    def __init__(self, settings: Settings):
        self.cipher = Fernet(settings.encryption_key.get_secret_value().encode("ascii"))
        self.lookup_key = bytes.fromhex(settings.email_lookup_key.get_secret_value())
        self.password_hasher = PasswordHash.recommended()

    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> str:
        return self.cipher.decrypt(value.encode("ascii")).decode("utf-8")

    def email_index(self, normalized_email: str) -> str:
        return hmac.new(
            self.lookup_key, normalized_email.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)
