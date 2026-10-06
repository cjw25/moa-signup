from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'members.db').as_posix()}"
    encryption_key: SecretStr
    email_lookup_key: SecretStr

    @field_validator("encryption_key")
    @classmethod
    def valid_encryption_key(cls, value: SecretStr) -> SecretStr:
        try:
            Fernet(value.get_secret_value().encode("ascii"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Run python scripts/setup_env.py to generate a Fernet key") from exc
        return value

    @field_validator("email_lookup_key")
    @classmethod
    def valid_lookup_key(cls, value: SecretStr) -> SecretStr:
        try:
            decoded = bytes.fromhex(value.get_secret_value())
        except ValueError as exc:
            raise ValueError("EMAIL_LOOKUP_KEY must be a 32-byte hex key") from exc
        if len(decoded) != 32:
            raise ValueError("EMAIL_LOOKUP_KEY must be a 32-byte hex key")
        return value
