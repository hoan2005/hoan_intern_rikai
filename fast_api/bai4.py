from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users(limit: int = 10, offset: int = 0):
    return {"limit": limit, "offset": offset}