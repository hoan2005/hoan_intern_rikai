import logging

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.controllers.auth_controller import router as auth_router
from app.controllers.collection_controller import router as collection_router
from app.controllers.note_controller import router as note_router
from app.core.config import settings
from app.core.errors import INVALID_REQUEST
from app.db.session import get_db

logger = logging.getLogger(__name__)

app = FastAPI(title="Mini Notion API")
app.include_router(auth_router)
app.include_router(collection_router)
app.include_router(note_router)


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": INVALID_REQUEST},
    )


@app.get("/", tags=["health"])
def check_database_connection(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.exception("Không thể kết nối đến cơ sở dữ liệu")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối đến cơ sở dữ liệu",
        ) from error

    return {"status": "ok", "database": "connected"}
