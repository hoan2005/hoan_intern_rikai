from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field,EmailStr

app = FastAPI()


class UserCreate(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr = Field(..., description="Phải đúng định dạng email")

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}
@app.post("/users", status_code=status.HTTP_201_CREATED,response_model=UserResponse)
def create_user(user: UserCreate):
   
    if user.email == "hoan@gmail.com":
       
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email này đã được đăng ký trong hệ thống!"
        )
    

    return user