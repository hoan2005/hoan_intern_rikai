from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from redis.asyncio import Redis
from app.routers import auth_routers
from app.routers import post_routers
from app.routers import user_routers
from app.database import Base, engine
from app.core.config import settings
from app.exceptions import register_exception_handlers
from app.middleware import register_request_logging
from app.rate_limit import register_rate_limiting
from app.response_format import register_global_response_format


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
    )
    application.state.redis = redis_client
    try:
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    title="thiết kế API backend",
    description=(
        "API quản lý người dùng, xác thực và bài viết. Tài liệu tương tác "
        "được cung cấp bởi Swagger UI tại `/docs`. Các API trả phản hồi theo "
        "envelope `{success, message, data}` khi thành công và "
        "`{success, message}` khi thất bại."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

register_rate_limiting(app)
register_request_logging(app)
register_global_response_format(app)
register_exception_handlers(app)
Base.metadata.create_all(bind=engine)

app.include_router(user_routers.router)
app.include_router(post_routers.router)
app.include_router(auth_routers.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Kiểm tra API đang hoạt động",
    description="Endpoint công khai trả lời lời chào và đường dẫn Swagger UI.",
    response_description="Thông báo chào mừng.",
    responses={
        200: {
            "description": "API đang hoạt động.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Success",
                        "data": {
                            "message": (
                                "Chào mừng đến với Mini CRUD API! "
                                "Hãy truy cập "
                                "/docs để sử dụng "
                                "Swagger UI."
                            )
                        },
                    }
                }
            },
        }
    },
)
def root():
    return {
        "message": (
            "Chào mừng đến với Mini CRUD API! Hãy truy cập /docs để sử dụng"
            " Swagger UI."
        )
    }
