# crud.py
# db에 직접 접근하여 create, read, update, delete 하는 함수를 관리하는 파일

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

import models, schemas

question_type = ["vote", "challenge", "normal"]
comment_type = ["text", "sound", "anything"]


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


def get_question_by_commentid(db: Session, comment_id: int):
    comment = get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="comment is not found")
    return db.query(models.Question).filter(models.Question.id == comment.question_id).first()


def get_comments_by_questionid(db: Session, question_id: int):
    return db.query(models.Comment).filter(models.Comment.question_id == question_id).all()


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).get(comment_id)


def get_valid_questions_by_userid(db: Session, user_id: int):
    return db.query(models.Question).filter(models.Question.user_id == user_id).filter(models.Question.is_deleted == False) \
        .filter(models.Question.type != "vote").filter(models.Question.expired == False).all()


def get_valid_votequestions_by_userid(db: Session, user_id: int):
    return db.query(models.Question).filter(models.Question.user_id == user_id).filter(models.Question.is_deleted == False) \
        .filter(models.Question.type == "vote").filter(models.Question.expired == False).all()


def get_expired_questions_by_userid(db: Session, user_id: int):
    return db.query(models.Question).filter(models.Question.is_deleted == False) \
        .filter(models.Question.user_id == user_id).filter(models.Question.expired == True).all()


def get_valid_comments(db: Session, user_id: int):
    valid_questions = get_valid_questions_by_userid(db, user_id)
    comments = []
    for q in valid_questions:
        if (datetime.now() - q.created_at).days >= 1:
            q.expired = True
            db.add(q)
            db.commit()
            db.refresh(q)
            continue
        db_comments = get_comments_by_questionid(db, question_id=q.id)
        comments += [c for c in db_comments if c.type == "text"]
    return comments


def get_valid_soundcomments(db: Session, user_id: int):
    valid_questions = get_valid_questions_by_userid(db, user_id)
    comments = []
    for q in valid_questions:
        if (datetime.now() - q.created_at).days >= 1:
            q.expired = True
            db.add(q)
            db.commit()
            db.refresh(q)
            continue
        db_comments = get_comments_by_questionid(db, question_id=q.id)
        comments += [c for c in db_comments if c.type == "sound"]
    return comments


def get_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user is not found")
    elif db_user.is_deleted:
        raise HTTPException(status_code=405, detail="user is deleted")
    return db_user


def get_question(db: Session, question_id: int) -> models.Question | None:
    return db.query(models.Question).filter(models.Question.id == question_id).first()


def get_valid_questions(db: Session, question_id: int):
    question = get_question(db=db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question is not found")

    if question.expired: # question의 expired가 True면
        raise HTTPException(status_code=404, detail="expired Link") # 예외발생
    else:
        if (datetime.now() - question.created_at).seconds / 3600 <= 24: # 24시간이 안 지났으면
            return question # 질문 반환
        else: # 24시간이 지났으면
            raise HTTPException(status_code=404, detail="expired Link")
            question.expired = True # question의 expired를 False로 변경
            db.commit()
            db.refresh(question)


def get_random_question(db: Session, question_type: str):
    return db.query(models.RandomQuestion).filter(models.RandomQuestion.type == question_type).all()


def get_questionid(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()
    
    
# question id가 일치하는 옵션 모두 리스트로 반환
def get_vote_options(db: Session, question_id: int):
    options = db.query(models.VoteOption).filter(models.VoteOption.question_id == question_id).all()
    return options


def create_user(db: Session, user: schemas.UserCreate):
    try:
        db_user = models.User(user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as ex:
        print(ex)
        return ex

def update_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter_by(insta_id=user.insta_id).first()
    if db_user == None:
        return 'insta_id_not_found'
    db_user.username = user.username
    db_user.full_name = user.full_name
    db_user.follower = user.follower
    db_user.following = user.following
    db_user.profile_image_url = user.profile_image_url
    db_user.is_deleted = False
    db_user.updated_at = datetime.now()

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter_by(id=user_id).first()
    if db_user == None:
        raise HTTPException(status_code=404, detail="user is not found")
    if db_user.is_deleted:
        raise HTTPException(status_code=405, detail="user is already deleted")

    db_user.is_deleted = True
    db_user.updated_at = datetime.now()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 해당 user가 가진 question까지 삭제
    delete_question_by_user_id(db, user_id)

    return {}


# question soft delete - user id로 삭제
def delete_question_by_user_id(db: Session, user_id: int):
    # user_id 해당되는 question데이터까지 삭제(soft)
    db_questions = db.query(models.Question).filter_by(user_id=user_id, is_deleted=False).all()
    
    if db_questions == None:
        raise HTTPException(status_code=404, detail="no questions in user data")
    for q in db_questions:
        q.is_deleted = True
        q.updated_at = datetime.now()
        db.add(q)
        db.commit()
        db.refresh(q)


# question soft delete - question id로 삭제
def delete_question_by_question_id(db: Session, question_id: int):
    db_question = db.query(models.Question).filter_by(id=question_id).first()
    if db_question == None:
        raise HTTPException(status_code=404, detail="question is not found")
    if db_question.is_deleted:
        raise HTTPException(status_code=405, detail="question is already deleted")

    db_question.is_deleted = True
    db_question.updated_at = datetime.now()
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return {}


#comment hard delete
def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter_by(id=comment_id).first()
    if db_comment == None:
        raise HTTPException(status_code=404, detail="comment is not found")

    db.delete(db_comment)
    db.commit()

    return {}
    

def create_question(db: Session, question: schemas.QuestionCreate):
    if(question.type in question_type):
        db_question = models.Question(question)
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
    for i in range(0, len(option)):  # 옵션의 개수만큼 vote comment에 저장
        db_vote_option = models.VoteOption(num=i + 1, content=option[i], question_id=question_id)
        db.add(db_vote_option)
        db.commit()
        db.refresh(db_vote_option)
        created_option.append(option[i])

    return created_option


def create_comment(db: Session, comment: schemas.CommentCreate):
    if get_question_comment_type(db, comment.question_id) not in [comment_type[0], comment_type[2]]:
        raise HTTPException(status_code=405, detail="unsupported comment_type")
    db_comment = models.Comment(content=comment.content, type=comment_type[0], question_id=comment.question_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def create_sound_comment(db: Session, question_id: int):
    if get_question_comment_type(db, question_id) not in [comment_type[1], comment_type[2]]:
        raise HTTPException(status_code=405, detail="unsupported comment_type")
    db_comment = models.Comment(content="", type=comment_type[1], question_id=question_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_sound_comment(db: Session, comment_id: int, content: str):
    db_voice_comment = db.query(models.Comment).get(comment_id)
    if db_voice_comment:
        db_voice_comment.content = content
        db.commit()
        db.refresh(db_voice_comment)

    return db_voice_comment

def get_question_comment_type(db: Session, question_id: int):
    return get_question(db=db, question_id=question_id).comment_type
