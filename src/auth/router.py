import os
from datetime import timedelta
from typing import Annotated, Dict
from fastapi import HTTPException, status, Depends, APIRouter, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.utils import authenticate_user, create_access_token
from src.database import get_async_session
from .models import User, Avatar
from .schemas import Token, UserCreate, UserSchema, UserChange
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, AVATARS_DIR
from .utils import write_to_disk, get_current_user, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication and registration"]
)


@router.post("/token/", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_async_session)
) -> Dict:
    """
    URL для получения токена для последующей авторизации
    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token,
            "token_type": "bearer"}


@router.post("/sign-up/", response_model=UserSchema)
async def create_user(
        new_user: UserCreate.form_body() = Depends(),
        file: UploadFile = File(default=None, description="Your avatar"),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    URL для регистрации новых пользователей
    """
    if file and file.headers.get('content-type') not in ('image/jpeg', 'image/jpg', 'image/png'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect file format. Acceptable - jpg, jpeg, png",
        )
    
    data = new_user.dict()
    password = data.pop('password')
    us: User = User(**data)
    us.set_password(password)
    
    if file:
        avatar_name = await write_to_disk(file)
        us.avatar = Avatar(src=avatar_name,
                           alt=f'{new_user.username}`s avatar')
    
    session.add(us)
    
    await session.commit()
    return us


@router.patch("/account/", response_model=UserSchema)
async def change_account(
        user_data: UserChange.form_body() = Depends(),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        file: UploadFile = File(default=None, description="Your avatar"),
) -> User:
    """
    URL для внесения изменений в аккаунт
    """
    data = user_data.dict()
    data = dict(filter(lambda item: item[1] is not None, data.items()))
    if not verify_password(data.pop('password'), current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect password",
        )
    
    u: User = await session.execute(select(User).where(User.id == current_user.id))
    u = u.scalars().first()
    last_avatar = u.avatar
    
    if data.get('new_password'):
        u.set_password(data.pop('new_password'))
    
    if file:
        avatar_name = await write_to_disk(file)
        u.avatar = Avatar(src=avatar_name,
                          alt=f'{u.username}`s avatar')
    
    if last_avatar:
        os.remove(os.path.join(AVATARS_DIR, last_avatar.src))
        await session.execute(delete(Avatar).where(Avatar.src == last_avatar.src))

    session.add(u)
    if data:
        await session.execute(update(User).values(**data).where(User.id == current_user.id))
    await session.commit()
    
    return u
