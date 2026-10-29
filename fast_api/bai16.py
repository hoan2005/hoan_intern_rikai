from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req, exc):
    errors = []
    for err in exc.errors():
        field = err['loc'][-1]
        msg = err['msg']

        if msg.startswith('Value error'):
            msg = msg.replace('Value error, ', '')

        errors.append({
            'field': field,
            'message': msg
        })
    return JSONResponse(status_code=422, content={'errors': errors})



class UserRegister(BaseModel):
  username: str
  age: int  

@app.post("/register")
def register_user(user: UserRegister):
  return {"success": True, "message": "Đăng ký thành công!", "data": user}