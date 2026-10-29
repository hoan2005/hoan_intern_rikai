from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


fake_users_db = [
    {"id": 1, "username": "alice"},
    {"id": 2, "username": "bob"},
    {"id": 3, "username": "charlie"}
]

class UserResponse(BaseModel):
    id: int
    username: str

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int):
  
    for user in fake_users_db:
        if user["id"] == user_id:
            return user 
    
   
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )