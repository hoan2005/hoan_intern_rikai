from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class UserCreate(BaseModel):
    id: int
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):

    return user
