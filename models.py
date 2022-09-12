# models.py
# db 테이블을 구성하는 파일

from sqlite3 import Timestamp
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, MetaData, Table
from sqlalchemy.orm import relationship

from database import Base

metadata = MetaData()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insta_id = Column(String(20), unique=True)
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    # user - question 1:N 관계 설정
    user_question = relationship("Question")


# user = Table(
#     "user",
#     metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True),
#     Column('insta_id', String(20), unique=True),
#     Column('created_date', TIMESTAMP),
#     Column('updated_date', TIMESTAMP),
# )


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500))
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String(1))
    expired = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    question_comment = relationship("Comment")
    question_vote_option = relationship("VoteOption")


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(1))
    content = Column(String(100))
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())


class VoteOption(Base):
    __tablename__ = "vote_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer)
    content = Column(String(500))
    count = Column(Integer)
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())



class RandomQuestion(Base):
    __tablename__ = "random_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500))
    type = Column(String(1))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

