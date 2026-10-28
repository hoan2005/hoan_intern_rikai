from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    name: str
    email: str
    age: int

@app.post("/users")
def create_user(user: UserCreate):
    return {
        "message": "User created successfully",
        "user": {
            "name": user.name,
            "email": user.email,
            "age": user.age
        }
    }