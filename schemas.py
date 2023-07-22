from typing import Optional
from pydantic import BaseModel, ConfigDict
from models import SexEnum


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
