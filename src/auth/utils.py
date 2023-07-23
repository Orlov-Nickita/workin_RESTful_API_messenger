import os
import uuid
from datetime import timedelta, datetime
from typing import Dict
import aiofiles
from fastapi import HTTPException, status, Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
from src.database import get_async_session
from .models import pwd_context
from .schemas import UserInDB, TokenData
from src.config import SECRET_KEY, ALGORITHM, AVATARS_DIR

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str):
    """
    Проверка пароля. Введенный пароль от пользователя сравнивается с хэшем пароля в БД
    
    Атрибуты:
    plain_password (str): Введенный пароль
    hashed_password (str): Хэш пароля в БД
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(username: str, session: AsyncSession) -> UserInDB:
    """
    Получение объекта пользователя с его хэшем пароля из БД
    
    Атрибуты:
    username (str): Никнейм пользователя
    session (AsyncSession): Асинхронная сессия для выполнения запросов к базе данных
    """
    a = await session.execute(select(User).where(User.username == username))
    a: User = a.scalars().first()
    if a:
        return UserInDB.from_orm(a)


async def authenticate_user(username: str, password: str, session: AsyncSession) -> UserInDB | bool:
    """
    Аутентификация пользователя
    
    Атрибуты:
    username (str): Никнейм пользователя
    password (str): Введенный пароль пользователя
    session (AsyncSession): Асинхронная сессия для выполнения запросов к базе данных
    """
    user = await get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: Dict, expires_delta: timedelta | None = None) -> str:
    """
    Создание токена доступа
    
    Атрибуты:
    data (Dict): Словарь с ключом sub и значением - никнейм пользователя
    expires_delta (timedelta | None = None): Время сгорания токена. По умолчанию None. Значение передается в минутах
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_async_session)) -> UserInDB:
    """
    Получение объекта текущего пользователя из базы данных
    
    Атрибуты:
    token (str): Токен авторизации пользователя.
    session (AsyncSession): Асинхронная сессия для выполнения запросов к базе данных
    
    Исключения:
    - HTTPException 401 UNAUTHORIZED: Если не удается проверить учетные данные пользователя.
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def write_to_disk(file: UploadFile) -> str:
    """
    Асинхронная функция скачивания файла
    
    Атрибуты:
    content (bytes): Байтовая строка файла
    file_path (str): Путь, куда скачиваем
    """
    avatar_name, avatar_extension = os.path.splitext(file.filename)
    avatar_path: str = os.path.join(AVATARS_DIR, f'{avatar_name}{avatar_extension}')
    
    if os.path.exists(avatar_path):
        avatar_name: str = avatar_name + '_' + str(uuid.uuid4())[:10]
        avatar_path: str = os.path.join(AVATARS_DIR, f'{avatar_name}{avatar_extension}')
    
    file_read = await file.read()
    async with aiofiles.open(avatar_path, mode='wb') as f:
        await f.write(file_read)
    
    return f'{avatar_name}{avatar_extension}'
