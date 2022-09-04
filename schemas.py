# schemas.py
# 테이블의 타입을 설정하는 파일

from sqlite3 import Timestamp


from pydantic import BaseModel # 객체 타입설정

# DB 에 넣을 때
class User(BaseModel):
    id: int # 자동생성
    insta_id: str
    created_at: Timestamp # db넣을 때 생성
    updated_at: Timestamp # db넣을 때 생성

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    insta_id: str

    class Config:
        orm_mode = True


class Question(BaseModel):
    id: int # 자동생성
    content: str
    user_id: int
    type: str
    expired: bool # 기본 값 false
    created_at: Timestamp # db넣을 때 생성
    updated_at: Timestamp # db넣을 때 생성

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    content: str
    user_id: int
    type: str

    class Config:
        orm_mode = True

class QuestionUpdate(BaseModel):   
    expired: bool

    class Config:
        orm_mode = True