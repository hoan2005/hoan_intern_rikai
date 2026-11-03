from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = error["loc"][-1]
            message = error["msg"]
            if message.startswith("Value error"):
                message = message.replace("Value error, ", "")
            errors.append({"field": field, "message": message})
        return JSONResponse(status_code=422, content={"errors": errors})
