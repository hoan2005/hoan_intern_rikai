from fastapi import FastAPI
from app.routers import auth_routers
from app.routers import post_routers
from app.routers import user_routers
from app.database import Base, engine
from app.exceptions import register_exception_handlers

app = FastAPI(
    title="thiết kế API backend",
    description="luyện tập kết nối đến database",
    version="1.0.0",
)

register_exception_handlers(app)
Base.metadata.create_all(bind=engine)

app.include_router(user_routers.router)
app.include_router(post_routers.router)
app.include_router(auth_routers.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": (
            "Chào mừng đến với Mini CRUD API! Hãy truy cập /docs để sử dụng"
            " Swagger UI."
        )
    }
