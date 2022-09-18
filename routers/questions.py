import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import schemas, crud
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
def create_vote_question(question: schemas.QuestionCreate, option: List[str], db: Session = Depends(get_db)):
    # 글자수 제한 검사
    if len(question.content) > 20:
        raise HTTPException(status_code=415, detail="exceeded length limit - vote question: 20")
    for op in option:
        if len(op) > 10:
            raise HTTPException(status_code=415, detail="exceeded length limit - vote option: 10")

    if not 2 <= len(option) <= 4:
        raise HTTPException(status_code=415, detail="number of options out of range")

    created_question = crud.create_question(db, question=question)

    # if len(created_option) < 1:
    #     raise HTTPException(status_code=404, detail="option creation failed")

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
    if len(question.content) > 40:
        raise HTTPException(status_code=415, detail="exceeded length limit - question: 40")

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



