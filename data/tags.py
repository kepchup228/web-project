import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('photo', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('photos.id')),
                                     sqlalchemy.Column('tag', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('tags.id'))
                                     )


class Tag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tags'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)

    photos = orm.relationship("Photo", secondary="association", back_populates="tags")