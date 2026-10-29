from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Tên phải có ít nhất 3 ký tự")
    email: EmailStr = Field(..., description="Phải đúng định dạng email")
    age: int = Field(..., ge=18, le=100, description="Tuổi phải từ 18 đến 100")

@app.post("/users")
def create_user(user: UserCreate):
    return {
        "message": "User created successfully",
        "data": user
    }