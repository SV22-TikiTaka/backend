# crud.py
# db에 직접 접근하여 create, read, update, delete 하는 함수를 관리하는 파일

from datetime import datetime
from re import L
from typing import List
from venv import create
from sqlalchemy.orm import Session
import models, schemas


def get_questions_by_userid(db: Session, user_id: int):
    return db.query(models.Question).filter(models.Question.user_id == user_id).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(insta_id=user.insta_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(content=question.content, user_id=question.user_id, type="n")
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# create question과 다른 점이 타입밖에 없음 - 하나의 메소드로 만들고 옵션 유무에 따라 다르게 저장되도록 하면 좋을듯
def create_vote_question(db: Session, vote: schemas.VoteCreate):
    db_question = models.Question(content=vote.content, user_id=vote.user_id, type="v")
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# 투표 질문 선택지 생성
def create_vote_comment(db: Session, question_id: int, option: List[str]):
    now = datetime.now()
    created_option = []
    for i in range(0, len(option)): #옵션의 개수만큼 vote comment에 저장
        db_vote_comment = models.VoteComment(num=i+1, content = option[i], count = 0
            , question_id = question_id, created_at = now, updated_at = now)
        db.add(db_vote_comment)
        db.commit()
        db.refresh(db_vote_comment)
        created_option.append(option[i])
        
    return created_option

