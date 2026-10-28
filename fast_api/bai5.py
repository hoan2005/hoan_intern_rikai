from fastapi import FastAPI


app = FastAPI()




@app.post("/users")
def create_user(user:dict):
    return {
        "message": "User created",
        "name": user["name"],
        "age": user["age"]
    }