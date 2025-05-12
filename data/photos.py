from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db_session import SqlAlchemyBase
from .photo_tags import photo_tags

class Photo(SqlAlchemyBase):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    is_private = Column(Boolean, default=False)

    user = relationship("User")
    comments = relationship("Comment", back_populates="photo", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=photo_tags, back_populates="photos")
