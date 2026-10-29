# product
from fastapi import APIRouter
product = APIRouter(prefix="/products", tags=["Products"])
@product.get("/")
def get_all_products():
  return [{"product_id": 1, "name": "Laptop"}, {"product_id": 2, "name": "Phone"}]
@product.get("/{product_id}")
def get_product_detail(product_id: int):
  return {"product_id": product_id, "name": "Laptop", "price": 1000}

#user
from fastapi import APIRouter
user = APIRouter(
    prefix="/users", 
    tags=["Users"],  
)
@user.get("/")
def get_all_users():
  return [{"username": "admin"}, {"username": "nguyen_van_a"}]
@user.get("/{user_id}")
def get_user_by_id(user_id: int):
  return {"user_id": user_id, "username": "nguyen_van_a"}


# file main
from fastapi import Depends, FastAPI
from router import user,products        

app = FastAPI()


app.include_router(user.user)
app.include_router(products.product)