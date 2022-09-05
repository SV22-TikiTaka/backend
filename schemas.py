# schemas.py
# 테이블의 타입을 설정하는 파일

from sqlite3 import Timestamp
from typing import Optional

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


class BaseTextComment(BaseModel):
    content: str


class TextCommentCreate(BaseTextComment):
    question_id: int


class TextComment(BaseTextComment):
    id: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성


class BaseSoundComment(BaseModel):
    url: str


class SoundCommentCreate(BaseSoundComment):
    question_id: int


class SoundComment(BaseSoundComment):
    id: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성


class BaseVoteComment(BaseModel):
    num: int
    content: String


class VoteCommentCreate(BaseVoteComment):
    question_id: int


class VoteComment(BaseVoteComment):
    id: int
    count: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성
