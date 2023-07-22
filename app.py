from typing import List

from fastapi import FastAPI
from sqlalchemy import select

from models import Base, User, Avatar, Message
from database import engine, session
from schemas import UserSchema

app = FastAPI(title='workin_messenger')


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.get('/users/', tags=["Users"], response_model=List[UserSchema])
async def get_user_by_username(username: str) -> List[User]:
    res = await session.execute(select(User).filter(User.username.like(f'%{username}%')))
    return res.scalars().all()
