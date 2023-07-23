import pydantic_core
from fastapi import FastAPI, Request, status
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse
from src.auth.router import router as auth_router
from src.messenger.router import router as mess_router

app = FastAPI(title='workin_messenger')
app.include_router(mess_router)
app.include_router(auth_router)


@app.exception_handler(IntegrityError)
async def my_exception_handler(request: Request, exc: IntegrityError):
    """
    Отлавливает ошибки IntegrityError, связанные с ошибками добавления записей в БД
    """
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": f'{exc}'})


@app.exception_handler(pydantic_core._pydantic_core.ValidationError)
async def my_exception_handler(request: Request, exc: pydantic_core._pydantic_core.ValidationError):
    """
    Отлавливает ошибки pydantic_core._pydantic_core.ValidationError
    """
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": f'{exc}'})
