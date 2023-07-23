from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()


engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция асинхронного генератора, которая возвращает асинхронный контекстный менеджер для сеанса для работы с
    асинхронным кодом и взаимодействия с базой данных.

    Возвращается:
    - Асинхронный генератор, который выдает объект асинхронного сеанса БД
    """
    async with async_session() as session:
        yield session