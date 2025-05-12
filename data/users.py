import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

# Пользователь и методы для работы с паролем
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)  # Электронная почта
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Хэш пароля
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # Дата

    photos = orm.relationship("Photo", back_populates="user")  # Связь с фотографиями

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'  # Строкой

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)  # Хэш пароля

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)  # Проверка пароля
