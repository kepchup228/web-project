from sqlalchemy import Table, Column, Integer, ForeignKey
from .db_session import SqlAlchemyBase
# Таблица для связи фото и тегов
photo_tags = Table('photo_tags', SqlAlchemyBase.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)
