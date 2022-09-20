import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import schemas, crud, models
from database import get_db


router = APIRouter(
    prefix="/api/v1/questions",
    tags=["questions"],
)


# B-4
# 원하는 type을 query parameter로 받아 해당 type인 질문을 랜덤으로 반환
@router.get('/random', response_model=schemas.RandomQuestion, status_code=200)
def show_random_question(type: str, db: Session = Depends(get_db)):
    questions = crud.get_random_question(db, question_type=type)
    if len(questions) == 0:
        raise HTTPException(status_code=404, detail="questions are not found")

    random.seed()
    idx = random.randint(0, len(questions) - 1)
    return questions[idx]


# F-2
# question 데이터 soft 삭제
@router.delete('/{question_id}', status_code=204)
def delete_question(question_id: int, db: Session=Depends(get_db)):
    return crud.delete_question_by_question_id(db, question_id)


# B-10
# 투표 질문 저장
@router.post('/vote/', status_code=201)
def create_vote_question(vote_with_option: schemas.VoteCreate, db: Session = Depends(get_db)):
    # 글자수 제한 검사
    if len(vote_with_option.content) > models.word_limit["Vote_content_limit"]:
        raise HTTPException(status_code=415, detail="exceeded length limit - vote question")
    for op in vote_with_option.option:
        if len(op) > models.word_limit["Vote_option_limit"]:
            raise HTTPException(status_code=415, detail="exceeded length limit - vote option")

    if not models.word_limit["Min_option_count"] <= len(vote_with_option.option) <= models.word_limit["Max_option_count"]:
        raise HTTPException(status_code=415, detail="number of options out of range")

    vote_question = schemas.BaseVote(content=vote_with_option.content, user_id=vote_with_option.user_id)
    created_question = crud.create_vote_question(db, vote_question=vote_question)
    created_option = crud.create_vote_option(db, created_question.id, vote_with_option.option)

    return {"question_id": created_question.id, "option": created_option}


# B-9
# question 생성에 필요한 정보를 보내면 DB에 저장
@router.post('/', response_model=schemas.Question, status_code=201)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    # 타입 검사
    if not crud.QuestionType.check_vaild_question_type(question.type):
        raise HTTPException(status_code=415, detail="unsupported question type")
    if question.type == crud.QuestionType.vote:
        raise HTTPException(status_code=415, detail="unsupported question type")
    if not crud.CommentType.check_vaild_comment_type(question.comment_type):
        raise HTTPException(status_code=415, detail="unsupported comment type")

    # 글자수 제한 검사
    if len(question.content) > models.word_limit["Question_content_limit"]:
        raise HTTPException(status_code=415, detail="exceeded length limit")

    return crud.create_question(db, question=question)


# D-10
# inbox에서 question 상세보기
@router.get('/{question_id}', response_model=schemas.Question, status_code=200)
def get_question(question_id: int,  db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question is not found")
    return question


# D-6
# user_id를 path variable로 받아서 user에 해당하는 질문들을 반환
@router.get('/history/{user_id}', response_model=List[schemas.Question], status_code=200)
def show_expired_questions(user_id: int, db: Session = Depends(get_db)):
    # user 존재 확인
    crud.get_user(db, user_id=user_id)

    questions = crud.get_expired_questions_by_userid(db, user_id=user_id)
    return questions


# C-2
# 링크 접속 시 질문 내용 반환
@router.get('/url', response_model=schemas.Question)
def get_question_from_url(question_id: int, db: Session = Depends(get_db)):
    return crud.get_valid_questions(db=db, question_id=question_id)



