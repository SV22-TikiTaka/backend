# main.py
# 서버 시작과 API들을 관리하는 파일?
import os, shutil, boto3
import random
from typing import List


from botocore.exceptions import ClientError
from fastapi import Depends, FastAPI, HTTPException, UploadFile, Form
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from starlette.middleware.cors import CORSMiddleware
import crud
from utils import check_db_connected
import models, schemas
from database import SessionLocal, engine
from voice_alteration import voice_alteration
import crud


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# DB
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def app_startup():
    await check_db_connected()
    db = SessionLocal()
    questions = crud.get_random_question(db, "challenge")
    if len(questions) == 0:
        crud.insert_questions(db)
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
    comments.sort(key=lambda x: x.created_at)
    return comments



# D-7
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 답변들을 반환
@app.get('/api/v1/users/{user_id}/comments/text', response_model=List[schemas.Comment], status_code=200)
def show_valid_comments(user_id: int, db: Session = Depends(get_db)):
    comments = crud.get_valid_comments(db, user_id=user_id)
    return comments


# D-8
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 음성답변들을 반환
@app.get('/api/v1/users/{user_id}/comments/sound', response_model=List[schemas.Comment], status_code=200)
def show_valid_sound_comments(user_id: int, db: Session = Depends(get_db)):
    comments = crud.get_valid_soundcomments(db, user_id=user_id)
    return comments


# D-9
# user_id를 path variable로 받아 해당 user의 유효한 질문들의 투표답변들을 반환
@app.get('/api/v1/users/{user_id}/comments/vote', response_model=List[schemas.VoteResult], status_code=200)
def show_valid_vote_comments(user_id: int, db: Session = Depends(get_db)):
    vote_questions = crud.get_valid_votequestions_by_userid(db, user_id=user_id)
    voteResults = []
    for question in vote_questions:
        vote_options = crud.get_vote_options(db, question.id)
        vote_option_contents = [vote_options[i].content for i in range(len(vote_options))]
        vote_count = [vote_options[i].count for i in range(len(vote_options))]
        updated_at = vote_options[0].updated_at
        voteResults.append(schemas.VoteResult(question_id=question.id, options=vote_option_contents, count=vote_count,
        created_at=question.created_at, updated_at=updated_at))

    return voteResults



# C-6
# .wav 파일과 question_id를 form 데이터로 받아 해당 파일 음성 변조해 s3 bucket에 파일 저장,  url도 db에 저장
@app.post('/api/v1/comments/voice', response_model=schemas.Comment, status_code=201)
def create_sound_comment(file: UploadFile, question_id: int = Form(), db: Session = Depends(get_db)):
    if crud.get_question(db, question_id=question_id) is None:
        raise HTTPException(status_code=404, detail="question is not found")

    comment = crud.create_sound_comment(db, question_id=question_id)
    if comment is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # temp 폴더 생성
    if not os.path.exists('temp'):
        os.mkdir('temp')

    # 클라이언트에서 보낸 음성 파일 저장
    file_path = "temp/" + str(comment.id) + ".wav"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 음성 변조 후, s3에 저장
    voice_alteration(file_path, comment.id)
    upload_file(file_path, str(comment.id))
    os.remove(file_path)

    # url update
    comment = crud.update_sound_comment(db, comment_id=comment.id,
                                        content=f"https://tikitaka-s3.s3.ap-northeast-2.amazonaws.com/{comment.id}")
    return comment




# B-4
# 원하는 type을 query parameter로 받아 해당 type인 질문을 랜덤으로 반환
@app.get('/api/v1/questions/random', response_model=schemas.RandomQuestion, status_code=200)
def show_random_question(type: str, db: Session = Depends(get_db)):
    questions = crud.get_random_question(db, question_type=type)
    if len(questions) == 0:
        raise HTTPException(status_code=404, detail="questions are not found")

    random.seed()
    idx = random.randint(0, len(questions) - 1)
    return questions[idx]


# user_id를 path variable로 받아서 해당 user의 정보를 반환
@app.get('/api/v1/users/{user_id}', response_model=schemas.User)
def show_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id=user_id)


# C-2
# 링크 접속 시 질문 내용 반환
@app.get('/api/v1/questions', response_model=schemas.Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    if crud.get_question(db, question_id=question_id) is None:
        raise HTTPException(status_code=404, detail="question is not found")
    return crud.get_question(db, question_id=question_id)


# C-3
# 링크 접속 시 투표 내용 반환
# @app.get('/api/v1/questions', response_model=schemas.Question)
# def get_vote_question(question_type: str, db: Session = Depends(get_db)):
#     return crud.get_vote_question(db, question_type=question_type)


# C-4
# 투표 답변(comment) 저장
@app.patch('/api/v1/comments/vote/{vote_comment_id}', response_model=schemas.VoteOption)
def update_vote_count(vote_comment_id: int, db: Session = Depends(get_db)):
    return crud.update_vote_count(db, vote_comment_id)


# # user 생성에 필요한 정보를 보내면 DB에 저장
# @app.post('/api/v1/users', response_model=schemas.User)
# def create_user(user: schemas.User, db: Session = Depends(get_db)):
#     return crud.create_user(db, user=user)


# B-9
# question 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/questions', response_model=schemas.Question)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    if(question.type not in crud.question_type or crud.question_type == "vote"):
        raise HTTPException(status_code=415, detail="unsupported question type")
    if(question.comment_type not in crud.comment_type):
        raise HTTPException(status_code=415, detail="unsupported comment type")
    return crud.create_question(db, question=question)


# B-10
# 투표 질문 저장
@app.post('/api/v1/questions/vote/{userId}')
def create_vote_question(question: schemas.QuestionCreate, option: List[str], db: Session = Depends(get_db)):
    created_question = crud.create_question(db, question=question)
    created_option = crud.create_vote_option(db, created_question.id, option)
    if (created_question == None):
        created_option = crud.create_vote_comment(db, created_question.id, option)
    if created_question is None:
        raise HTTPException(status_code=404, detail="question creation failed")
    if len(created_option) < 1:
        raise HTTPException(status_code=404, detail="option creation failed")
    return {"question_id": created_question.id, "option": created_option}


# B-8
# 질문 공유를 위한 url을 생성
@app.get('/api/v1/questions/url', response_model=str)
def get_question_url(user_id: int, question_id: int, db: Session = Depends(get_db)):
    insta_id = crud.get_user(db, user_id=user_id).insta_id
    return f'http://localhost:3000/{insta_id}/{question_id}'


# C-5
# 텍스트 답변 저장
@app.post('/api/v1/comments/text', response_model=schemas.Comment)
def store_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    if len(comment.content) > 100:
        raise HTTPException(status_code=404, detail="글자수 초과")
    elif crud.get_question(db, question_id=comment.question_id) is None:
        raise HTTPException(status_code=404, detail="question is not found")
    return crud.create_comment(db, comment=comment)

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

# D-3
# comment_id를 path variable로 받아 해당 comment를 반환
@app.get('/api/v1/comments/{comment_id}', response_model=schemas.Comment, status_code=200)
def show_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = crud.get_comment(db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="comment is not found")
    return comment

# D-5
# 투표 질문 클릭시 투표 옵션 및 결과 반환
@app.get('/api/v1/comments/vote/{question_id}', response_model=schemas.VoteResult, status_code=200)
def show_vote_result(question_id: int, db: Session=Depends(get_db)):
    
    vote_question = crud.get_question(db, question_id=question_id)
    vote_options = crud.get_vote_options(db, question_id)
    vote_option_contents = [vote_options[i].content for i in range(len(vote_options))]
    vote_count = [vote_options[i].count for i in range(len(vote_options))]
    updated_at = vote_options[0].updated_at #옵션객체.updated_at 셋 중 가장최근시간

    return schemas.VoteResult(options=vote_option_contents, count=vote_count,
        created_at=vote_question.created_at, updated_at=updated_at)

    
    