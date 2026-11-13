from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str | None = Field(default=None, max_length=10000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("Tiêu đề ghi chú không được để trống")
        return title


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = Field(default=None, max_length=10000)
    is_pinned: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        title = value.strip()
        if not title:
            raise ValueError("Tiêu đề ghi chú không được để trống")
        return title

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> "NoteUpdate":
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Tiêu đề ghi chú không được để trống")
        if "is_pinned" in self.model_fields_set and self.is_pinned is None:
            raise ValueError("Trạng thái ghim không được để trống")
        return self


class NoteTagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    title: str
    body: str | None
    is_pinned: bool
    created_at: datetime | None
    updated_at: datetime | None
    tags: list[NoteTagRead]


class NoteList(BaseModel):
    items: list[NoteRead]
    total: int
    limit: int
    offset: int
