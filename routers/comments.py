from typing import List

import boto3
import shutil

from botocore.exceptions import ClientError
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import schemas, crud, voice_alteration
from database import get_db

router = APIRouter(
    prefix="/api/v1/comments",
    tags=["comments"],
)

client_s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)


# S3 Bucket
def upload_file(location, file):
    try:
        client_s3.upload_file(
            location,
            os.getenv('AWS_S3_BUCKET_NAME'),
            file,
            ExtraArgs={'ContentType': 'audio/wav'}
        )
    except ClientError as e:
        print(f'Credential error => {e}')
    except Exception as e:
        print(f"Another error => {e}")


# F-3
# comment 데이터 hard 삭제
@router.delete('/{comment_id}', status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    return crud.delete_comment(db, comment_id)


# D-7
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 답변들을 반환
@router.get('/users/{user_id}/text', response_model=List[schemas.Comment], status_code=200)
def show_valid_comments(user_id: int, db: Session = Depends(get_db)):
    comments = crud.get_valid_comments(db, user_id=user_id, type=crud.CommentType.text)
    return comments


# D-8
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 음성답변들을 반환
@router.get('/users/{user_id}/sound', response_model=List[schemas.Comment], status_code=200)
def show_valid_sound_comments(user_id: int, db: Session = Depends(get_db)):
    comments = crud.get_valid_comments(db, user_id=user_id, type=crud.CommentType.sound)
    return comments


# D-9
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 투표답변들을 반환
@router.get('/users/{user_id}/vote', response_model=List[schemas.VoteResult], status_code=200)
def show_valid_vote_options(user_id: int, db: Session = Depends(get_db)):
    vote_questions = crud.get_valid_votequestions_by_userid(db, user_id=user_id)
    # user_id check
    if len(vote_questions) < 1:
        raise HTTPException(status_code=404, detail="Non Existent user_id")

    voteResults = []
    for question in vote_questions:
        vote_options = crud.get_vote_options(db, question.id)
        if len(vote_options) < 1:
            raise HTTPException(status_code=404, detail="Empty vote option")
        vote_option_contents = [vote_options[i].content for i in range(len(vote_options))]
        vote_count = [vote_options[i].count for i in range(len(vote_options))]

        updated_time_list = sorted(
            [vote_options[i].updated_at for i in range(len(vote_options))])  # 옵션객체.updated_at 셋 중 가장최근시간
        updated_at = updated_time_list[len(vote_options) - 1]  # 가장 최근에 업데이트된 시간

        voteResults.append(schemas.VoteResult(question_id=question.id, options=vote_option_contents, count=vote_count,
                                              created_at=question.created_at, updated_at=updated_at))

    return voteResults


# D-2
# question_id를 path variable로 받아서 해당 question에 해당하는 comment들을 반환
@router.get('/questions/{question_id}', response_model=List[schemas.Comment], status_code=200)
def show_comments(question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question is not found")

    comments = crud.get_comments_by_questionid(db, question_id=question_id)
    # comments.sort(key=lambda x: x.created_at)
    return comments


# D-5
# 투표 질문 클릭시 투표 옵션 및 결과 반환
@router.get('/vote/{question_id}', response_model=schemas.VoteResult, status_code=200)
def show_vote_result(question_id: int, db: Session = Depends(get_db)):
    vote_question = crud.get_question(db, question_id=question_id)
    if vote_question.type != crud.QuestionType.vote:
        raise HTTPException(status_code=404, detail="not vote question")
    vote_options = crud.get_vote_options(db, question_id)
    vote_option_contents = [vote_options[i].content for i in range(len(vote_options))]
    vote_count = [vote_options[i].count for i in range(len(vote_options))]

    updated_time_list = sorted(
        [vote_options[i].updated_at for i in range(len(vote_options))])  # 옵션객체.updated_at 셋 중 가장최근시간
    updated_at = updated_time_list[len(vote_options) - 1]  # 가장 최근에 업데이트된 시간

    return schemas.VoteResult(question_id=question_id, options=vote_option_contents, count=vote_count,
                              created_at=vote_question.created_at, updated_at=updated_at)


# D-3
# comment_id를 path variable로 받아 해당 comment를 반환
@router.get('/{comment_id}', response_model=schemas.Comment, status_code=200)
def show_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = crud.get_comment(db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="comment is not found")
    return comment


# C-4
# 투표 답변(comment) 저장
@router.put('/vote/{vote_comment_id}', response_model=schemas.VoteOption)
def update_vote_count(vote_comment_id: int, db: Session = Depends(get_db)):
    return crud.update_vote_count(db, vote_comment_id)


# C-5
# 텍스트 답변 저장
@router.post('/text', response_model=schemas.Comment, status_code=201)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    if len(comment.content) > 100:
        raise HTTPException(status_code=404, detail="글자수 초과")
    elif crud.get_question(db, question_id=comment.question_id) is None:
        raise HTTPException(status_code=404, detail="question is not found")
    return crud.create_comment(db, comment=comment)


# C-6
# .wav 파일과 question_id를 form 데이터로 받아 해당 파일 음성 변조해 s3 bucket에 파일 저장,  url도 db에 저장
@router.post('/voice', response_model=schemas.Comment, status_code=201)
def create_sound_comment(file: UploadFile, question_id: int = Form(), db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question is not found")

    if question.comment_type == crud.CommentType.text:
        raise HTTPException(status_code=415, detail="Unsupported comment type.")

    comment = crud.create_sound_comment(db, question_id=question_id)

    # temp 폴더 생성
    if not os.path.exists('./temp'):
        os.mkdir('./temp')

    # 클라이언트에서 보낸 음성 파일 저장
    file_path = "temp/" + str(comment.id) + ".wav"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 음성 변조 후, s3에 저장
    voice_alteration.voice_alteration(file_path, comment.id)
    upload_file(file_path, str(comment.id))
    os.remove(file_path)

    # url update
    comment = crud.update_sound_comment(db, comment_id=comment.id,
                                        content=f"https://tikitaka-s3.s3.ap-northeast-2.amazonaws.com/{comment.id}")
    return comment
