import datetime
import enum
from passlib.context import CryptContext
from phonenumbers import is_possible_number, parse
from phonenumbers.phonenumberutil import NumberParseException
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import validates, relationship, Mapped
from src.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SexEnum(enum.Enum):
    """
    Класс для перечисления, представляющий возможные значения атрибута "Пол"
    
    Атрибуты:
    - Man: представляет значение "Мужчина"
    - Woman: представляет значение "Женщина"
    """
    Man = 'Man'
    Woman = 'Woman'


class Avatar(Base):
    """
    Класс модели Аватар
    
    Поля:
    id (int): Первичный ключ таблицы
    src (str): Относительный путь
    alt (str): Альтернативный текст для изображения аватара, когда изображение по какой-то причине не загружено
    created_at (datetime.дата-время): Дата создания
    """
    __tablename__ = 'Avatar'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    src = Column(String, nullable=False)
    alt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    user: Mapped["User"] = relationship('User', back_populates='avatar', lazy='joined', cascade='all, delete-orphan')


class User(Base):
    """
    Класс модели Пользователь
    
    Поля:
    id (int): Первичный ключ
    username (str): Никнейм
    password_hash (str): Хэш пароля
    first_name (str): Имя
    last_name (str): Фамилия
    phone (str): Телефон
    sex (SexEnum): Пол. Предполагается только 2 варианта
    avatar_id (int): Ссылка на первичный ключ из таблицы Аватар
    email (str): Электронная почта
    """
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String(20), nullable=False)
    sex = Column(Enum(SexEnum), nullable=False)
    avatar_id = Column(Integer, ForeignKey('Avatar.id'))
    email = Column(String, nullable=False)
    
    avatar: Mapped["Avatar"] = relationship('Avatar', back_populates='user', lazy='joined', uselist=False)
    
    def set_password(self, password: str):
        """
        Хэширует пароль и присваивает экземпляру класса результат хэширования для последующего сохранения в БД
        """
        self.password_hash = pwd_context.hash(password)
    
    @validates('phone')
    def validate_phone_number(self, key, phone_number):
        """
        Проверяет формат номера телефона
        """
        try:
            is_possible_number(parse(phone_number))
        except NumberParseException:
            raise ValueError('Incorrect phone number format')
        return phone_number
