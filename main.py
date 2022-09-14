# main.py
# 서버 시작과 API들을 관리하는 파일?
import os, shutil, boto3, requests, random
from typing import List

from dotenv import load_dotenv
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

# 환경변수 로드
load_dotenv()

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


# ----------------------------------------------------
# 인스타 로그인 및 프로필 정보 가져오기

app_id = os.getenv('INSTA_APP_ID')
secret_id = os.getenv('INSTA_APP_SECRET_ID')
redirect_url = "https://localhost:8000/insta"
authorize_url = f"https://api.instagram.com/oauth/authorize?client_id=\
    {app_id}&redirect_uri={redirect_url}&scope=user_profile,user_media&response_type=code"
get_short_token_url = "https://api.instagram.com/oauth/access_token"
get_user_name_url = "https://graph.instagram.com/me?fields=username&access_token="
get_user_info_url = "https://i.instagram.com/api/v1/users/web_profile_info/?username="
get_long_token_url = f"https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret={secret_id}&access_token="
refresh_token_url = "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token="

# 인스타 연동 페이지로 이동
@app.get("/api/v1/authorize")
async def go_to_authorize_page():
    return RedirectResponse(url=authorize_url)


# 인스타 연동 성공시 리디렉션되는 API, 발행된 code로 장기 토큰 얻기
@app.get("/insta")
def get_insta_code(code: str, db: Session = Depends(get_db)):
    if code is None:
        raise HTTPException(status_code=404, detail="code is not found")
    short_token = get_short_token(code)
    long_token = get_long_token(short_token)['long_access_token']
    user_info = get_user_info(long_token)
    user_create_data = schemas.UserCreate(insta_id=user_info['insta_id'], name=user_info['name'],\
         follower=user_info['follower'], following=user_info['following'], \
            profile_image_url=user_info['profile_image_url'])
    # result_info = create_user_by_user_info(user_create_data, db)
    # return result_info


# 단기 토큰 얻기
def get_short_token(code: str):
    data = {
        'client_id': app_id,
        'client_secret': secret_id,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_url
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'charset': 'UTF-8', 'Accept': '*/*'}
    try:
        res = requests.post(get_short_token_url, headers = headers, data = data)
        return res.json()["access_token"]
    except Exception as ex:
        print(ex.args)


# 장기 토큰 얻기
def get_long_token(short_access_token: str):
    try:
        res = requests.get(get_long_token_url+short_access_token)
        long_access_token = res.json()['access_token']
        expires_in = res.json()['expires_in']
        return {'long_access_token': long_access_token, 'expires_in': expires_in}
    except Exception as ex:
        print(ex.args)


# 엑세스 토큰으로 user info 얻기
def get_user_info(access_token: str):
    try:
        username = requests.get(get_user_name_url + access_token).json()["username"]
        
        # 만약 헤더 오류 시 아래 api로 대체
        # user_info = requests.get(f'https://www.instagram.com/web/search/topsearch/?query={username}')
        
        # 헤더 정보에 대해서는 좀 더 알아보고 나중에 수정
        headers = {
            'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 \
                    (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)'
        }
        # username으로 user 정보 가져오는 api 호출
        user_info = requests.get(get_user_info_url + username, headers=headers).json()['data']['user']

        name = user_info['full_name']
        follower = user_info['edge_followed_by']['count']
        following = user_info['edge_follow']['count']
        profile_image_url = user_info['profile_pic_url']
        return {'insta_id': username, 'name': name, 'follower': follower, 'following': following,\
             'profile_image_url': profile_image_url}
    except Exception as ex:
        print(str(ex.args))

def get_refresh_token(long_access_token: str):
    res = requests.get(refresh_token_url+long_access_token)
    return res.json()['access_token']

@app.post('/api/v1/check', status_code=200)
def find_access_token():
    return 0

def create_user_by_user_info(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user=user)

# ----------------------------------------------------

# D-6
# user_id를 path variable로 받아서 user에 해당하는 질문들을 반환
@app.get('/api/v1/users/{user_id}/questions', response_model=List[schemas.Question], status_code=200)
def show_expired_questions(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user is not found")

    questions = crud.get_expired_questions_by_userid(db, user_id=user_id)
    return questions


# D-2
# question_id를 query parameter로 받아서 해당 question에 해당하는 comment들을 반환
@app.get('/api/v1/users/comments', response_model=List[schemas.Comment], status_code=200)
def show_comments(question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id=question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question is not found")

    comments = crud.get_comments_by_questionid(db, question_id=question_id)
    # comments.sort(key=lambda x: x.created_at)
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
        
        updated_time_list = sorted([vote_options[i].updated_at for i in range(len(vote_options))]) #옵션객체.updated_at 셋 중 가장최근시간
        updated_at = updated_time_list[len(vote_options)-1] #가장 최근에 업데이트된 시간
    
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
    return crud.get_valid_questions(db=db, question_id=question_id)

# C-4
# 투표 답변(comment) 저장
@app.patch('/api/v1/comments/vote/{vote_comment_id}', response_model=schemas.VoteOption)
def update_vote_count(vote_comment_id: int, db: Session = Depends(get_db)):
    return crud.update_vote_count(db, vote_comment_id)



# user 생성에 필요한 정보를 보내면 DB에 저장
@app.post('/api/v1/users', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # return crud.create_user(db, user=user)
    return create_user_by_user_info(user, db)


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
    
    updated_time_list = sorted([vote_options[i].updated_at for i in range(len(vote_options))]) #옵션객체.updated_at 셋 중 가장최근시간
    updated_at = updated_time_list[len(vote_options)-1] #가장 최근에 업데이트된 시간
    
    return schemas.VoteResult(question_id=question_id, options=vote_option_contents, count=vote_count,
        created_at=vote_question.created_at, updated_at=updated_at)

    
    