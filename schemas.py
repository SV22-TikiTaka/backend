# schemas.py
# 테이블의 타입을 설정하는 파일

from sqlite3 import Timestamp
from typing import List, Optional
from pydantic import BaseModel  # 객체 타입설정


class UserBase(BaseModel):
    insta_id: str  # user 생성 api 호출시 자동으로 부여
    username: str  # user 생성 api 호출시 자동으로 부여
    full_name: str  # user 생성 api 호출시 자동으로 부여
    follower: int  # user 생성 api 호출시 자동으로 부여
    following: int  # user 생성 api 호출시 자동으로 부여
    profile_image_url: str  # user 생성 api 호출시 자동으로 부여


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int  # 자동 생성
    is_deleted: bool  # 기본값 false
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    content: str
    user_id: int
    type: str
    comment_type: str


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    id: Optional[int]
    type: Optional[str]
    expired: bool


class Question(QuestionBase):
    id: int  # 자동 생성
    expired: bool  # 기본 값 false
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
    question_id: int


class CommentCreate(BaseComment):
    pass


class Comment(BaseComment):
    id: int
    type: str
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class BaseVoteOption(BaseModel):
    num: int
    content: str
    question_id: int or None


class CreateVoteOption(BaseVoteOption):
    pass


class VoteOption(BaseVoteOption):
    id: int
    count: int
    created_at: Timestamp  # db 넣을 때 생성
    updated_at: Timestamp  # db 넣을 때 생성

    class Config:
        orm_mode = True


class VoteResult(BaseModel):
    question_id: int
    options: List[str]
    count: List[int]
    created_at: Timestamp  # question 생성시간
    updated_at: Timestamp  # 마지막 투표 시간

    class Config:
        orm_mode = True
