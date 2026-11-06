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


class PostCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề bài viết")
    content: str = Field(..., description="Nội dung bài viết")
    category: str | None = Field(
        None, max_length=100, description="Danh mục bài viết"
    )
    published: bool = Field(False, description="Trạng thái xuất bản")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Bắt đầu với FastAPI",
                    "content": "FastAPI giúp xây dựng API Python nhanh chóng.",
                    "category": "Công nghệ",
                    "published": True,
                }
            ]
        }
    )

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> str:
        return _validate_title(value)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: object) -> str:
        return _validate_content(value)

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
    category: str | None = Field(None, description="Danh mục mới")
    published: bool | None = Field(None, description="Trạng thái xuất bản mới")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Cập nhật bài viết FastAPI",
                    "published": True,
                }
            ]
        }
    )

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> str:
        return _validate_title(value)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: object) -> str:
        return _validate_content(value)

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Bắt đầu với FastAPI",
                    "content": "FastAPI giúp xây dựng API Python nhanh chóng.",
                    "user_id": 7,
                    "category": "Công nghệ",
                    "published": True,
                    "created_at": "2026-01-01T10:00:00Z",
                }
            ]
        },
    )


class PaginatedPostResponse(BaseModel):
    page: int = Field(..., description="Trang hiện tại")
    limit: int = Field(..., description="Số bài viết tối đa trên một trang")
    total: int = Field(..., description="Tổng số bài viết phù hợp")
    items: list[PostResponse] = Field(
        ..., description="Các bài viết của trang"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "page": 1,
                    "limit": 10,
                    "total": 1,
                    "items": [
                        {
                            "id": 1,
                            "title": "Bắt đầu với FastAPI",
                            "content": (
                                "FastAPI giúp xây dựng API Python nhanh chóng."
                            ),
                            "user_id": 7,
                            "category": "Công nghệ",
                            "published": True,
                            "created_at": "2026-01-01T10:00:00Z",
                        }
                    ],
                }
            ]
        }
    )
