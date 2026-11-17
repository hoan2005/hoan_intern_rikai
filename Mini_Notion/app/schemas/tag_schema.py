from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Tên thẻ không được để trống")
        return name


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagList(BaseModel):
    items: list[TagRead]
    total: int
    limit: int
    offset: int