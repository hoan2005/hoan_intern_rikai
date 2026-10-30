from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
  username: str = Field(
      ...,
      min_length=3,
      max_length=50,
      description="Tên người dùng",
      json_schema_extra={
          "error_msg": "Tên người dùng phải từ 3 đến 50 ký tự."
      },
  )
  email: EmailStr = Field(
      ..., description="Địa chỉ email hợp lệ", json_schema_extra={"error_msg": "Email không hợp lệ."}
  )


class UserCreate(UserBase):
  password: str = Field(
      ...,
      min_length=6,
      description="Mật khẩu ít nhất 6 ký tự",
      json_schema_extra={"error_msg": "Mật khẩu phải có ít nhất 6 ký tự."},
  )


class UserUpdate(BaseModel):
  username: str | None = Field(
      None, min_length=3, max_length=50, description="Tên người dùng mới"
  )
  email: EmailStr | None = Field(None, description="Email mới")
  password: str | None = Field(None, min_length=6, description="Mật khẩu mới")


class UserResponse(UserBase):
  id: int = Field(..., description="ID định danh người dùng")

  class Config:
    from_attributes = True