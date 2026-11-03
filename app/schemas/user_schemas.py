from pydantic import BaseModel, EmailStr, Field, field_validator


def _validate_username(value: str) -> str:
    if len(value) < 3:
        raise ValueError("Tên người dùng phải có ít nhất 3 ký tự.")
    if len(value) > 50:
        raise ValueError("Tên người dùng không được vượt quá 50 ký tự.")
    return value


def _validate_password(value: str) -> str:
    if len(value) < 6:
        raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")
    return value


def _validate_email(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("""Email phải có dạng gồm chữ và số @gmail.com,
            chỉ dùng chữ cái và chữ số trước @.""")

    local_part, separator, domain = value.partition("@")
    has_letter = any(character.isalpha() for character in local_part)
    has_number = any(character.isdigit() for character in local_part)
    if (
        not separator
        or domain.lower() != "gmail.com"
        or not local_part.isascii()
        or not local_part.isalnum()
        or not has_letter
        or not has_number
    ):
        raise ValueError("""Email phải có dạng gồm chữ và số @gmail.com,
            chỉ dùng chữ cái và chữ số trước @.""")
    return value


class UserBase(BaseModel):
    username: str = Field(..., description="Tên người dùng")
    email: EmailStr = Field(..., description="Địa chỉ email hợp lệ")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return _validate_username(value)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email(value)


class UserCreate(UserBase):
    password: str = Field(..., description="Mật khẩu ít nhất 6 ký tự")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password(value)


class UserUpdate(BaseModel):
    username: str | None = Field(None, description="Tên người dùng mới")
    email: EmailStr | None = Field(None, description="Email mới")
    password: str | None = Field(None, description="Mật khẩu mới")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        return _validate_username(value) if value is not None else None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        return _validate_email(value) if value is not None else None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        return _validate_password(value) if value is not None else None


class UserResponse(UserBase):
    id: int = Field(..., description="ID định danh người dùng")

    class Config:
        from_attributes = True
