from fastapi import Depends, FastAPI

app = FastAPI()


def get_current_user():
  user_info = {"username": "admin", "email": "admin@example.com"}
  return user_info


@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
  
  return {"status": "success", "data": current_user}