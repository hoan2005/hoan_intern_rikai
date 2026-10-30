from fastapi import FastAPI
from router import user as user_router

app = FastAPI(
    title="Mini CRUD API - Quản lý người dùng",
    description=(
        "Ứng dụng mẫu quản lý người dùng với FastAPI, Pydantic và chia tách thư"
        " mục rõ ràng."
    ),
    version="1.0.0",
)

# Đăng ký router
app.include_router(user_router.router)


@app.get("/", tags=["Root"])
def root():
  return {
      "message": (
          "Chào mừng đến với Mini CRUD API! Hãy truy cập /docs để sử dụng"
          " Swagger UI."
      )
  }