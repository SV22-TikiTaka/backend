# schemas.py
# 테이블의 타입을 설정하는 파일

from ast import Str
from re import S
from sqlite3 import Timestamp
from typing import List, Optional

from pydantic import BaseModel  # 객체 타입설정


class UserBase(BaseModel):
    insta_id: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int  # 자동 생성
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    content: str
    user_id: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    id: Optional[int]
    type: Optional[str]
    expired: bool


class Question(QuestionBase):
    id: int  # 자동 생성
    expired: bool  # 기본 값 false
    type: str
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class RandomQuestion(BaseModel):
    id: int
    content: str
    type: str
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class VoteCreate(QuestionCreate):
    option: List[str]

class BaseComment(BaseModel):
    content: str
    type: str


class CommentCreate(BaseComment):
    pass


class Comment(BaseComment):
    id: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class VoteComment(BaseModel):
    question_id: int
    id: int
    count: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True

# class VoteOption(BaseModel):
#     question_id: int
#     option = List[str]

#     class Config:
#         orm_mode = True
#         arbitrary_types_allowed = True


