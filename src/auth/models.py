import re
import datetime
import enum
from phonenumbers import is_possible_number, parse
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import validates, relationship, Mapped

from src.database import Base


class SexEnum(enum.Enum):
    """
    TODO
    """
    MAN = 'Man'
    WOMAN = 'Woman'


class Avatar(Base):
    """
    TODO
    """
    __tablename__ = 'Avatar'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    src = Column(String, nullable=False)
    alt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    user: Mapped["User"] = relationship('User', back_populates='avatar', lazy='joined', cascade='all, delete-orphan')


class User(Base):
    """
    TODO
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
    
    # def set_password(self, password: str):
    #     """
    #     TODO
    #     """
    #     self.password_hash = pwd_context.hash(password)
    #
    # def verify_password(self, password: str) -> bool:
    #     """
    #     TODO
    #     """
    #     return pwd_context.verify(password, self.password_hash)
    
    def __repr__(self):
        return f"User: {self.last_name} {self.first_name}"
    
    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        """
        TODO
        Проверка формата номера телефона
        :param key:
        :param phone_number:
        :return:
        """
        res = is_possible_number(parse(phone_number))
        if not res:
            raise ValueError('Некорректный формат номера телефона')
        
        return phone_number
    
    @validates("email")
    def validate_email(self, key, address):
        """
        TODO
        :param key:
        :param address:
        :return:
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, address):
            raise ValueError("Некорректный формат E-mail")
        return address
