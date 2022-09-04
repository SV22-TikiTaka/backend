from datetime import datetime
from typing import List
from fastapi import FastAPI

from fastapi.params import Depends
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

# API형식은 일단 임시로 짠거라 나중에 바꾸면 될거같아요
# user_id를 path variable로 받아서 user에 해당하는 질문들을 반환
@app.get('/api/v1/questions/{user_id}', response_model=List[schemas.Question])
def show_questions(user_id: int, db: Session=Depends(get_db)):
    questions = db.query(models.Question).filter_by(user_id=user_id).all()
    return questions

# user_id를 path variable로 받아서 해당 user의 정보를 반환
@app.get('/api/v1/users/{user_id}', response_model=schemas.User)
def show_user(user_id: int, db: Session=Depends(get_db)):
    user = db.query(models.User).filter_by(id=user_id).first()
    return user

# user 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/users', response_model=schemas.User)
def create_user(enter: schemas.CreateUser, db: Session=Depends(get_db)):
    now = datetime.now()
    user = models.User(insta_id = enter.insta_id, created_date=now, updated_date=now)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# question 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/questions', response_model=schemas.Question)
def create_question(enter: schemas.CreateQuestion, db: Session=Depends(get_db)):
    now = datetime.now()
    question = models.Question(content = enter.content, user_id = enter.user_id, type='n', expired=False, created_date=now, updated_date=now)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

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