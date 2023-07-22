from datetime import date
from pydantic import BaseModel
from models import SexEnum


class AvatarSchema(BaseModel):
    id: int
    src: str
    alt: str
    # created_at: date


class UserSchema(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    sex: SexEnum
    avatar_id: int
    email: str
    avatar: AvatarSchema
    