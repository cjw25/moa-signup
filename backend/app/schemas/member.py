import unicodedata
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=12, max_length=128)
    password_confirmation: SecretStr = Field(min_length=1, max_length=128)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        if isinstance(value, str):
            value = unicodedata.normalize("NFC", value.strip())
            if any(unicodedata.category(char).startswith("C") for char in value):
                raise ValueError("이름에 제어 문자를 사용할 수 없습니다.")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def trim_email(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Product policy: email addresses are treated as case-insensitive.
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_is_not_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("공백만으로 된 비밀번호는 사용할 수 없습니다.")
        return value

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, value: SecretStr, info: ValidationInfo) -> SecretStr:
        password = info.data.get("password")
        if password is not None and value.get_secret_value() != password.get_secret_value():
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return value


class SignupResponse(BaseModel):
    id: str
    created_at: datetime
    message: str = "회원가입이 완료되었습니다."
