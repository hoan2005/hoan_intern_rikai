from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_title(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Tiêu đề phải là chuỗi ký tự.")
    value = value.strip()
    if not value:
        raise ValueError("Tiêu đề không được để trống.")
    if len(value) > 255:
        raise ValueError("Tiêu đề không được vượt quá 255 ký tự.")
    return value


def _validate_content(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Nội dung phải là chuỗi ký tự.")
    value = value.strip()
    if not value:
        raise ValueError("Nội dung không được để trống.")
    return value


def _validate_user_id(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("ID người dùng phải là số nguyên dương.")
    if isinstance(value, float) and not value.is_integer():
        raise ValueError("ID người dùng phải là số nguyên dương.")
    try:
        user_id = int(value)
    except (TypeError, ValueError):
        raise ValueError("ID người dùng phải là số nguyên dương.") from None
    if user_id <= 0:
        raise ValueError("ID người dùng phải là số nguyên dương.")
    return user_id


class PostCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề bài viết")
    content: str = Field(..., description="Nội dung bài viết")
    user_id: int = Field(..., description="ID người tạo bài viết")
    category: str | None = Field(
        None, max_length=100, description="Danh mục bài viết"
    )
    published: bool = Field(False, description="Trạng thái xuất bản")

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> str:
        return _validate_title(value)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: object) -> str:
        return _validate_content(value)

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value: object) -> int:
        return _validate_user_id(value)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Danh mục phải là chuỗi ký tự.")
        value = value.strip()
        if not value:
            raise ValueError("Danh mục không được để trống.")
        if len(value) > 100:
            raise ValueError("Danh mục không được vượt quá 100 ký tự.")
        return value


class PostUpdate(BaseModel):
    title: str | None = Field(None, description="Tiêu đề mới")
    content: str | None = Field(None, description="Nội dung mới")
    user_id: int | None = Field(None, description="ID người dùng mới")
    category: str | None = Field(None, description="Danh mục mới")
    published: bool | None = Field(None, description="Trạng thái xuất bản mới")

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> str:
        return _validate_title(value)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: object) -> str:
        return _validate_content(value)

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value: object) -> int:
        return _validate_user_id(value)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Danh mục phải là chuỗi ký tự.")
        value = value.strip()
        if not value:
            raise ValueError("Danh mục không được để trống.")
        if len(value) > 100:
            raise ValueError("Danh mục không được vượt quá 100 ký tự.")
        return value


class PostResponse(BaseModel):
    id: int = Field(..., description="ID bài viết")
    title: str
    content: str
    user_id: int
    category: str | None
    published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedPostResponse(BaseModel):
    page: int
    limit: int
    total: int
    items: list[PostResponse]
