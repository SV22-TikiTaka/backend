# crud.py
# db에 직접 접근하여 create, read, update, delete 하는 함수를 관리하는 파일
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from enum import Enum, auto

import models, schemas

# StrEnum을 상속받으면 CommentType.text 가 그대로 "text" 가 됨
class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class CommentType(StrEnum):
    ''' 질문의 답변타입 열겨형 변수 '''
    text = auto()
    sound = auto()
    anything = auto()
    def check_vaild_comment_type(type_name: str):
        ''' 입력받은 타입이 있는 타입이면 TRUE, 아니면 FALSE '''
        try:
            return CommentType[type_name] != None
        except:
            return False
    def compare_two_type(input_type: str, check_type: str):
        ''' input_type이 check_type이나 anything이면 true 아니면 FALSE '''
        try:
            return input_type in [CommentType[check_type], CommentType.anything]
        except:
            return False

class QuestionType(StrEnum):
    ''' 질문타입 열겨형 변수 '''
    vote = auto()
    challenge = auto()
    normal = auto()
    def check_vaild_question_type(type_name: str):
        ''' 입력받은 타입이 있는 타입이면 TRUE, 아니면 FALSE '''
        try:
            return QuestionType[type_name] != None
        except:
            return False



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


def get_comment(db: Session, comment_id: int) -> models.Comment | None:
    return db.query(models.Comment).get(comment_id)


def get_valid_questions_by_userid(db: Session, user_id: int) -> List[models.Question] | None:
    return db.query(models.Question).filter(models.Question.user_id == user_id).filter(models.Question.is_deleted == False) \
        .filter(models.Question.type != QuestionType.vote).filter(models.Question.expired == False).all()


def get_valid_votequestions_by_userid(db: Session, user_id: int) -> List[models.Question] | None:
    return db.query(models.Question).filter(models.Question.user_id == user_id).filter(models.Question.is_deleted == False) \
        .filter(models.Question.type == QuestionType.vote).filter(models.Question.expired == False).all()



def get_expired_questions_by_userid(db: Session, user_id: int) -> List[models.Question] | None:
    return db.query(models.Question).filter(models.Question.is_deleted == False) \
        .filter(models.Question.user_id == user_id).filter(models.Question.expired == True).all()


def get_valid_comments(db: Session, user_id: int, type: str) -> List[models.Comment] | None:
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
        comments += [c for c in db_comments if c.type == type]
    return comments


# def get_valid_soundcomments(db: Session, user_id: int):
#     valid_questions = get_valid_questions_by_userid(db, user_id)
#     comments = []
#     for q in valid_questions:
#         if (datetime.now() - q.created_at).days >= 1:
#             q.expired = True
#             db.add(q)
#             db.commit()
#             db.refresh(q)
#             continue
#         db_comments = get_comments_by_questionid(db, question_id=q.id)
#         comments += [c for c in db_comments if c.type == "sound"]
#     return comments


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

    if question.expired:  # question의 expired가 True면
        raise HTTPException(status_code=404, detail="expired Link")  # 예외발생
    elif (datetime.now() - question.created_at).seconds / 3600 <= 24: # 24시간이 안 지났으면
        return question # 질문 반환
    else: # 24시간이 지났으면
        question.expired = True # question의 expired를 False로 변경
        db.add(question)
        db.commit()
        db.refresh(question)
        raise HTTPException(status_code=404, detail="expired Link")


def get_random_question(db: Session, question_type: str):
    return db.query(models.RandomQuestion).filter(models.RandomQuestion.type == question_type).all()


# question id가 일치하는 옵션 모두 리스트로 반환
def get_vote_options(db: Session, question_id: int) -> List[models.VoteOption] | None:
    options = db.query(models.VoteOption).filter(models.VoteOption.question_id == question_id).all()
    return options


def create_user(db: Session, user: schemas.UserCreate) -> models.User | None:
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
        return -1 # 'insta_id_not_found'
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
        return
    for q in db_questions:
        q.is_deleted = True
        q.updated_at = datetime.now()
        db.add(q)
        db.commit()
        db.refresh(q)


# question soft delete - question id로 삭제
def delete_question_by_question_id(db: Session, question_id: int):
    db_question = db.query(models.Question).filter_by(id=question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="question is not found")
    if db_question.is_deleted:
        raise HTTPException(status_code=405, detail="question is already deleted")

    db_question.is_deleted = True
    db_question.updated_at = datetime.now()
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return {}


# comment hard delete
def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter_by(id=comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="comment is not found")

    db.delete(db_comment)
    db.commit()
    db.refresh(db_comment)

    return {}


# def create_question(db: Session, question: schemas.QuestionCreate):
#     db_question = models.Question(question)
#     db_question.user_id
#
#     if db_question is None:
#         raise HTTPException(status_code=404, detail="Non Existent Question")
#
#     elif db_question.type not in question_type:
#         raise HTTPException(status_code=415, detail="unsupported question type")
#
#     db.add(db_question)
#     db.commit()
#     db.refresh(db_question)
#     return db_question

# 유효성 검사 추가
def create_question(db: Session, question: schemas.QuestionCreate):

    # get_user 안에 user_id, is_delete 체크하는 코드가 있습니다
    user_check = get_user(db=db, user_id=question.user_id)

    # QuestionType check
    if QuestionType.check_vaild_question_type(question.type):
        db_question = models.Question(question)
    else:
        raise HTTPException(status_code=415, detail="unsupported question type")

    if len(question.content) >= models.word_limit["Question_content_limit"]:  # content 길이 검사
        raise HTTPException(status_code=404, detail="글자수 초과")

    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def update_vote_count(db: Session, vote_option_id: int) -> models.VoteOption | None:
    db_vote_option = db.query(models.VoteOption).filter_by(id=vote_option_id).first()
    if db_vote_option is None:
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

    if get_question(db=db, question_id=question_id) is None:
        raise HTTPException(status_code=404, detail="Non existent Question")

    for i in range(0, len(option)):  # 옵션의 개수만큼 vote comment에 저장
        db_vote_option = models.VoteOption(num=i + 1, content=option[i], question_id=question_id)
        db.add(db_vote_option)
        db.commit()
        db.refresh(db_vote_option)
        created_option.append(option[i])

    return created_option


def create_comment(db: Session, comment: schemas.CommentCreate) -> models.Comment | None:
    if not CommentType.compare_two_type(get_question_comment_type(db, comment.question_id), CommentType.text):
        raise HTTPException(status_code=405, detail="unsupported comment_type")
    db_comment = models.Comment(content=comment.content, type=CommentType.text, question_id=comment.question_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def create_sound_comment(db: Session, question_id: int):
    if not CommentType.compare_two_type(get_question_comment_type(db, question_id), CommentType.sound):
        raise HTTPException(status_code=405, detail="unsupported comment_type")
    db_comment = models.Comment(content="", type=CommentType.sound, question_id=question_id)
    if db_comment is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
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
