from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Tên bộ sưu tập không được để trống")
        return name


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        name = value.strip()
        if not name:
            raise ValueError("Tên bộ sưu tập không được để trống")
        return name

    @model_validator(mode="after")
    def validate_name_not_null(self) -> "CollectionUpdate":
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Tên bộ sưu tập không được để trống")
        return self


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None


class CollectionList(BaseModel):
    items: list[CollectionRead]
    total: int
    limit: int
    offset: int
