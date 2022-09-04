# models.py
# db 테이블을 구성하는 파일

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insta_id = Column(String(20), unique=True)
    created_date = Column(DateTime)
    updated_date = Column(DateTime)
    
    # user - question 1:N 관계 설정
    user_question = relationship("Question")


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500))
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String(1))
    expired = Column(Boolean)
    created_date = Column(DateTime)
    updated_date = Column(DateTime)