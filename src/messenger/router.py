from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy import select, func
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
                               current_user: User = Depends(get_current_user)
                               ) -> List[User]:
    """
    URL для поиска пользователей по никнейму
    """
    res = await session.execute(select(User)
                                .filter(func.lower(User.username).like(func.lower(f'%{username}%'))
                                        )
                                )
    return res.scalars().all()

@router.post('/messages/send/', response_model=MessageOutSchema)
async def send_message(message: MessagePostSchema,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: User = Depends(get_current_user)) -> Message:
    """
    URL для отправки сообщения
    """
    data = {
        'sender_id': current_user.id,
        **message.dict()
    }
    new_message: Message = Message(**data)
    session.add(new_message)
    await session.commit()
    return new_message
