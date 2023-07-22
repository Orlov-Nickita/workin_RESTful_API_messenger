from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.auth.models import SexEnum


class AvatarSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    src: str
    alt: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    sex: SexEnum
    email: str
    avatar: Optional[AvatarSchema]


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(UserSchema):
    password_hash: str


class TokenData(BaseModel):
    username: str | None = None
