from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    return {"endpoint": "users"}

@app.get("/products")
def get_products():
    return {"endpoint": "products"}