from typing import Optional
from fastapi import HTTPException, Form
from phonenumbers import is_possible_number, parse
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import BaseModel, ConfigDict, constr, EmailStr, field_validator
from fastapi import status

from src.auth.models import SexEnum


class AvatarSchema(BaseModel):
    """
    Схема модели Аватар
    
    Атрибуты:
    src (str): Относительный путь
    alt (str): Альтернативный текст для изображения аватара, когда изображение по какой-то причине не загружено
    """
    model_config = ConfigDict(from_attributes=True)
    
    src: str
    alt: str


class BaseUserSchema(BaseModel):
    """
    Базовая схема модели Пользователь
    
    Атрибуты:
    username (str): Никнейм
    first_name (str): Имя
    last_name (str): Фамилия
    phone (str): Телефон
    sex (SexEnum): Пол. Предполагается только 2 варианта
    email (str): Электронная почта
    """
    username: str
    first_name: str
    last_name: str
    phone: str
    sex: SexEnum
    email: EmailStr
    
    @field_validator('phone')
    def phone_validator(cls, v):
        """
        Проверка номера телефона на соответствие международному стандарту
        
        Атрибуты:
        v (str): Номер телефона
        """
        try:
            is_possible_number(parse(v))
        except NumberParseException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Incorrect phone number format",
            )
        return v


class UserSchema(BaseUserSchema):
    """
    Основная схема модели Пользователь. Наследуется от базовой схемы, дополняясь полями id и avatar
    
    Атрибуты:
    id (int): Первичный ключ
    avatar: Отношение один-к-одному, позволяющее обращаться к модели Автара посредством python-объектов
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    avatar: Optional[AvatarSchema]


class Token(BaseModel):
    """
    Схема Токена.
    
    Атрибуты:
    access_token (str): Сформированный токен доступа
    token_type (str): Тип токена
    """
    access_token: str
    token_type: str


class UserInDB(UserSchema):
    """
    Схема модели Пользователь. Наследуется от основной схемы, дополняясь хэшем пароля
    
    Атрибуты:
    password_hash (str): Хэш пароля
    """
    password_hash: str


class TokenData(BaseModel):
    """
    Схема Токена.
    
    Атрибуты:
    username (str): Никнейм пользователя, для которого изготавливается токена
    """
    username: str | None = None


class UserCreate(BaseUserSchema):
    """
    Cхема модели Пользователь для осуществления регистрации. Наследуется от базовой схемы, дополняясь полем password
    
    Атрибуты:
    password (str): Пароль, который присылает пользователь
    """
    password: constr(strip_whitespace=True, min_length=8)
    
    @classmethod
    def form_body(cls):
        """
        Изменяет сигнатуру класса, заменяя все параметры объектом Form(...)
        """
        cls.__signature__ = cls.__signature__.replace(
            parameters=[
                arg.replace(default=Form(...))
                for arg in cls.__signature__.parameters.values()
            ]
        )
        return cls


class UserChange(BaseModel):
    """
    Cхема модели Пользователь для внесения изменений в аккаунт

    Атрибуты:
    username (str): Никнейм
    first_name (str): Имя
    last_name (str): Фамилия
    phone (str): Телефон
    sex (SexEnum): Пол. Предполагается только 2 варианта
    email (str): Электронная почта
    """
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    sex: Optional[SexEnum]
    email: Optional[EmailStr]
    password: constr(strip_whitespace=True, min_length=8)
    new_password: Optional[constr(strip_whitespace=True, min_length=8)]
    
    @classmethod
    def form_body(cls):
        """
        Изменяет сигнатуру класса, заменяя все параметры объектом Form(...)
        """
        cls.__signature__ = cls.__signature__.replace(
            parameters=[
                arg.replace(default=Form(default=None))
                if arg.name != 'password' else arg.replace(default=Form())
                for arg in cls.__signature__.parameters.values()
            ]
        )
        return cls
