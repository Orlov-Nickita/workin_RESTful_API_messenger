from sqlalchemy import Column, Integer, ForeignKey, Text
from src.auth.models import Base


class Message(Base):
    """
    Класс модели Пользователь
    
    Поля:
    id (int): Первичный ключ
    sender_id (int): Ссылка на первичный ключ из таблицы Пользователь. Символизирует отправителя
    recipient_id (int): Ссылка на первичный ключ из таблицы Пользователь. Символизирует получателя
    content (str): Текст сообщения
    """
    __tablename__ = 'Message'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    content = Column(Text, nullable=False)
