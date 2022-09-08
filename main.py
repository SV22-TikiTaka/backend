# main.py
# 서버 시작과 API들을 관리하는 파일?

from typing import List
from fastapi import Depends, FastAPI, HTTPException
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from starlette.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# 접속시 자동으로 문서페이지로 이동
@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


# D-6
# user_id를 path variable로 받아서 user에 해당하는 질문들을 반환
@app.get('/api/v1/users/{user_id}/questions', response_model=List[schemas.Question], status_code=200)
def show_questions(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user is not found")

    questions = crud.get_questions_by_userid(db, user_id=user_id)
    return questions


# D-2
# question_id를 query parameter로 받아서 해당 question에 해당하는 comment들을 반환
@app.get('/api/v1/users/comments', response_model=List[schemas.Comment], status_code=200)
def show_comments(question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question is not found")

    comments = crud.get_comments_by_questionid(db, question_id=question_id)
    comments.sort(key=lambda x:x.created_at)
    return comments


# user_id를 path variable로 받아서 해당 user의 정보를 반환
@app.get('/api/v1/users/{user_id}', response_model=schemas.User)
def show_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id=user_id)


# user 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/users', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user=user)


# question 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/questions', response_model=schemas.Question)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db, question=question)

# B-8
# 질문 공유를 위한 url을 생성
@app.get('/api/v1/questions/url', response_model=str)
def get_question_url(user_id: int, question_id: int, db: Session = Depends(get_db)):
    insta_id = crud.get_user(db, user_id=user_id).insta_id
    return f'http://localhost:3000/{insta_id}/{question_id}'

@app.post('/api/v1/comments/text', response_model = schemas.Comment)
def store_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return crud.create_comment(db, comment = comment)


# 나중에 참고용 으로 일단 주석처리
# @app.put('/users/{user_id}', response_model=schemas.User)
# def update_users(user_id: int, enter: schemas.UserUpdate, db: Session=Depends(get_db)):
#     user = db.query(models.User).filter_by(id=user_id).first( )
#     user.fullname=enter.fullname
#     db.commit()
#     db.refresh(user)
#     return user

# @app.delete('/users/{user_id}', response_model=schemas.response)
# def delete_users(user_id: int, db: Session=Depends(get_db)):
#     user = db.query(models.User).filter_by(id=user_id).first( )
#     db.delete(user)
#     db.commit()
#     response = schemas.response(message="Successfully removed!")
#     return response
