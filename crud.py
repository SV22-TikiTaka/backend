# crud.py
# db에 직접 접근하여 create, read, update, delete 하는 함수를 관리하는 파일

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
