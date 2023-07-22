from pydantic import BaseModel


class MessagePostSchema(BaseModel):
    recipient_id: int
    content: str


class MessageOutSchema(MessagePostSchema):
    id: int
    sender_id: int

