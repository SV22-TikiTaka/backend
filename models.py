# models.py
# db 테이블을 구성하는 파일

from sqlite3 import Timestamp
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, MetaData
from sqlalchemy.orm import relationship

from database import Base

import schemas

metadata = MetaData()
word_limit = {"User_name_limit": 30, "Question_content_limit": 40, "Comment_content_limit": 100,
              "Vote_option_limit": 10}


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insta_id = Column(String(word_limit["User_name_limit"]), unique=True) # 인스타 에서 관리하는 숫자형태의 id, user 구분을 위해 사용
    username = Column(String(word_limit["User_name_limit"])) # 인스타 id 길이 제한이 30자 라서 수정
    full_name = Column(String(word_limit["User_name_limit"]))
    follower = Column(Integer)
    following = Column(Integer)
    profile_image_url = Column(String(500)) # 제 url 길이가 440자라서 여유있게 했습니다
    is_deleted = Column(Boolean)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __init__(self, user: schemas.UserCreate):
        self.insta_id = user.insta_id
        self.username = user.username
        self.full_name = user.full_name
        self.follower = user.follower
        self.following = user.following
        self.profile_image_url = user.profile_image_url
        self.is_deleted = False
        self.created_at = Timestamp.now()
        self.updated_at = self.created_at


    # user - question 1:N 관계 설정
    user_question = relationship("Question")



class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(word_limit["Question_content_limit"]))
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String(20))
    comment_type = Column(String(20))
    expired = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    question_comment = relationship("Comment")
    question_vote_option = relationship("VoteOption")

    def __init__(self, question: schemas.QuestionCreate):
        self.content = question.content
        self.user_id = question.user_id
        self.type = question.type
        self.comment_type = question.comment_type
        self.expired = False
        self.is_deleted = False
        self.created_at = Timestamp.now()
        self.updated_at = self.created_at


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20))
    content = Column(String(word_limit["Comment_content_limit"]))
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    def __init__(self, content: str, type: str, question_id: int):
        self.content = content
        self.type = type
        self.question_id = question_id
        self.created_at = Timestamp.now()
        self.updated_at = self.created_at


class VoteOption(Base):
    __tablename__ = "vote_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer)
    content = Column(String(word_limit["Vote_option_limit"]))
    count = Column(Integer)
    question_id = Column(Integer, ForeignKey("question.id"))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    def __init__(self, num: int, content: str, question_id: int):
        self.num = num
        self.content = content
        self.count = 0
        self.question_id = question_id
        self.created_at = Timestamp.now()
        self.updated_at = self.created_at


class RandomQuestion(Base):
    __tablename__ = "random_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(word_limit["Question_content_limit"]))
    type = Column(String(20))
    created_at = Column(TIMESTAMP, default=Timestamp.now())
    updated_at = Column(TIMESTAMP, default=Timestamp.now())

    def __init__(self, content: str, type: str):
        self.content = content
        self.type = type
        self.created_at = Timestamp.now()
        self.updated_at = self.created_at