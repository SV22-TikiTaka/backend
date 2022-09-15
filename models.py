# models.py
# db 테이블을 구성하는 파일

from sqlite3 import Timestamp
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, MetaData
from sqlalchemy.orm import relationship

from database import Base

metadata = MetaData()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insta_id = Column(String(30), unique=True) # 인스타 에서 관리하는 숫자형태의 id, user 구분을 위해 사용
    username = Column(String(30)) # 인스타 id 길이 제한이 30자 라서 수정
    full_name = Column(String(30))
    follower = Column(Integer)
    following = Column(Integer)
    profile_image_url = Column(String(500)) # 제 url 길이가 440자라서 여유있게 했습니다
    is_deleted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    # user - question 1:N 관계 설정
    user_question = relationship("Question")


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(40))
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String(20))
    comment_type = Column(String(20))
    expired = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    question_comment = relationship("Comment")
    question_vote_option = relationship("VoteOption")


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20))
    content = Column(String(100))
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())


class VoteOption(Base):
    __tablename__ = "vote_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer)
    content = Column(String(10))
    count = Column(Integer)
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())


class RandomQuestion(Base):
    __tablename__ = "random_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(40))
    type = Column(String(20))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

