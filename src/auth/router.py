import os
import uuid
from datetime import timedelta
from typing import Annotated, Dict
from fastapi import HTTPException, status, Depends, APIRouter, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.utils import authenticate_user, create_access_token
from src.database import get_async_session
from .models import User, Avatar
from .schemas import Token, UserCreate, UserSchema
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, AVATARS_DIR
from .utils import write_to_disk

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
        avatar_name, avatar_extension = os.path.splitext(file.filename)
        avatar_path: str = os.path.join(AVATARS_DIR, f'{avatar_name}{avatar_extension}')
        
        if os.path.exists(avatar_path):
            avatar_name: str = avatar_name + '_' + str(uuid.uuid4())[:10]
            avatar_path: str = os.path.join(AVATARS_DIR, f'{avatar_name}{avatar_extension}')
        
        file_read = await file.read()
        await write_to_disk(file_read, avatar_path)
        
        us.avatar = Avatar(src=avatar_name,
                           alt=f'{new_user.username}`s avatar')
    
    session.add(us)
    
    await session.commit()
    return us
