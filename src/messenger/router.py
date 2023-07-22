from typing import List, Dict
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
from src.auth.schemas import UserSchema
from src.messenger.models import Message
from src.auth.utils import get_current_user
from src.database import get_async_session
from .schemas import MessagePostSchema, MessageOutSchema

router = APIRouter(
    prefix="",
    tags=["Messenger"]
)


@router.get('/users/search/', response_model=List[UserSchema])
async def get_user_by_username(username: str,
                               session: AsyncSession = Depends(get_async_session),
                               current_user: User = Depends(get_current_user)) -> List[User]:
    """TODO"""
    res = await session.execute(select(User).filter(User.username.like(f'%{username}%')))
    return res.scalars().all()


# @router.middleware(IntegrityError)
# async def my_exception_handler(request: Request, exc: IntegrityError):
#     """TODO"""
#     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
#                         content={"error": f'{exc}'})

#
# @router.get("/myself_info/", tags=['Other'], response_model=UserSchema)
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     """TODO"""
#     return current_user


@router.post('/messages/send/', response_model=MessageOutSchema)
async def send_message(message: MessagePostSchema,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(get_current_user)) -> Message:
    """TODO"""
    data = {
        'sender_id': current_user.id,
        **message.dict()
    }
    new_message: Message = Message(**data)
    session.add(new_message)
    await session.commit()
    return new_message
