from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.messenger.router import router as mess_router

app = FastAPI(title='workin_messenger')
app.include_router(mess_router)
app.include_router(auth_router)
