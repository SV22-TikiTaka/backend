# crud.py
# db에 직접 접근하여 create, read, update, delete 하는 함수를 관리하는 파일

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

import models, schemas

question_type = ["vote", "challenge", "normal"]


def insert_questions(db: Session):
    file = open("questions.txt", "r", encoding="utf-8")
    lines = file.readlines()
    for idx, line in enumerate(lines):
        line = line.split(",")
        row = models.RandomQuestion(content=line[0], type=line[1].strip())
        db.add(row)
    db.commit()
    file.close()


def get_questions_by_userid(db: Session, user_id: int):
    return db.query(models.Question).filter(models.Question.user_id == user_id).all()


def get_comments_by_questionid(db: Session, question_id: int):
    return db.query(models.Comment).filter(models.Comment.question_id == question_id).all()


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).get(comment_id)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()


def get_random_question(db: Session, question_type: str):
    return db.query(models.RandomQuestion).filter(models.RandomQuestion.type == question_type).all()


def get_questionid(db:Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

#question id가 일치하는 옵션 모두 리스트로 반환
def get_vote_options(db: Session, question_id: int):
    options = db.query(models.VoteOption).filter(models.VoteOption.question_id == question_id).all()
    return options
    
    #question id가 일치하는 옵션 객체를 리스트에 넣기
    

# def create_user(db: Session, user: schemas.UserCreate):
#     db_user = models.User(insta_id=user.insta_id)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


def create_question(db: Session, question: schemas.QuestionCreate):
    if(question.type in question_type):
        db_question = models.Question(content=question.content, user_id=question.user_id, type=question.type)
    else:
        raise HTTPException(status_code=415, detail="unsupported question type")
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def update_vote_count(db: Session, vote_option_id: int):
    db_vote_option = db.query(models.VoteOption).filter_by(id=vote_option_id).first()
    if db_vote_option == None:
        raise HTTPException(status_code=404, detail="vote_option not found")
    db_vote_option.count += 1
    db_vote_option.updated_at = datetime.now()
    db.add(db_vote_option)
    db.commit()
    db.refresh(db_vote_option)
    return db_vote_option


# 투표 질문 선택지 생성
def create_vote_option(db: Session, question_id: int, option: List[str]):
    created_option = []
    for i in range(0, len(option)): #옵션의 개수만큼 vote comment에 저장
        db_vote_option = models.VoteOption(num=i + 1, content = option[i], count = 0
                                           , question_id = question_id)
        db.add(db_vote_option)
        db.commit()
        db.refresh(db_vote_option)
        created_option.append(option[i])
        
    return created_option
    

def create_comment(db: Session, comment: schemas.CommentCreate):
    db_comment = models.Comment(content = comment.content, question_id = comment.question_id, type ="n")
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def create_sound_comment(db: Session, question_id: int):
    db_comment = models.Comment(content="", type='s', question_id=question_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_sound_comment(db: Session, comment_id: int, content: str):
    db_voice_comment = db.query(models.Comment).get(comment_id)
    # update todo item with the given task (if an item with the given id was found)
    if db_voice_comment:
        db_voice_comment.content = content
        db.commit()
        db.refresh(db_voice_comment)
    # check if todo item with given id exists. If not, raise exception and return 404 not found response
    # raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return db_voice_comment

