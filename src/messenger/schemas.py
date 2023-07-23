from pydantic import BaseModel


class MessagePostSchema(BaseModel):
    """
    Cхема модели Сообщение

    Атрибуты:
    recipient_id (int): ID пользователя - Получатель сообщения
    content (str): Текст сообщения
    """
    recipient_id: int
    content: str


class MessageOutSchema(MessagePostSchema):
    """
    Схема модели Пользователь. Наследуется от схемы MessagePostSchema, дополняясь полями id и sender_id

    Атрибуты:
    id (int): Первичный ключ, который присвоен сообщению в БД после отправки
    sender_id (int): ID пользователя - Отправитель сообщения
    """
    id: int
    sender_id: int
