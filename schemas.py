# schemas.py
# 테이블의 타입을 설정하는 파일

from sqlite3 import Timestamp
from typing import Optional
from pydantic import BaseModel  # 객체 타입설정


class User(BaseModel):
    id: int  # 자동 생성
    insta_id: str # user 생성 api 호출시 자동으로 부여
    name: str # user 생성 api 호출시 자동으로 부여
    follower: int # user 생성 api 호출시 자동으로 부여
    following: int # user 생성 api 호출시 자동으로 부여
    profile_image_url: str # user 생성 api 호출시 자동으로 부여
    is_deleted: bool # 기본값 
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    content: str
    user_id: int
    type: str
    comment_type = str


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    id: Optional[int]
    type: Optional[str]
    expired: bool


class Question(QuestionBase):
    id: int  # 자동 생성
    expired: bool  # 기본 값 false
    is_deleted: bool
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


class BaseComment(BaseModel):
    content: str
    type: str
    question_id: int


class CommentCreate(BaseComment):
    pass


class Comment(BaseComment):
    id: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class VoteOption(BaseModel):
    question_id: int
    id: int
    count: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True




