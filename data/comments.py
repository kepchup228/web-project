from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase

class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, ForeignKey('photos.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String, nullable=False)

    photo = relationship("Photo", back_populates="comments")
    user = relationship("User")
