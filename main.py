# main.py
# 서버 시작과 API들을 관리하는 파일?

from os import access
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from starlette.responses import RedirectResponse

from starlette.middleware.cors import CORSMiddleware
from utils import check_db_connected
import models, crud, insta
from database import SessionLocal, engine
from routers import users, comments, questions

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 환경변수 로드
load_dotenv()

app.include_router(users.router)
app.include_router(questions.router)
app.include_router(comments.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# A-1
# 인스타그램 로그인 페이지로 이동한다.
# 앱 접속 시 프론트에 유효한 토큰이 없다면 인스타 연동 페이지로 이동
@app.get("/api/v1/authorize")
def go_to_authorize_page():
    return RedirectResponse(url=insta.authorize_url)


# A-2
# 장기 토큰을 리프레쉬 하여 반환. 만료된 토큰이면 A-1 API로 리디렉션된다.
# 프론트에서 발급 받은 토큰 저장 후 user_info_change_by_access_token 호출
@app.get("/api/v1/refresh-token", status_code=200)
def get_refresh_token(long_access_token: str = Header(default=None)):
    res = insta.get_refresh_token(long_access_token=long_access_token)
    # 토큰이 만료되었다면
    if res == -1:
        go_to_authorize_page()

    elif res['expires_in'] < 30:
        go_to_authorize_page()
    else: return res


# A-8
# 인스타 연동 시 리디렉션되는 API, 발행된 code로 장기 토큰을 발급한다.
# 프론트에서 발급 받은 토큰 저장 후 user_info_change_by_access_token 호출해야함
# 프론트에서 직접 호출할 일이 없으므로 문서에서 숨김
@app.get("/api/v1/insta/redirection", include_in_schema=False)
def get_insta_code(code=None, error=None, error_description=None):
    # 인증 실패 시
    if error is not None:
        raise HTTPException(status_code=421, detail=error_description)
        # 적절한 페이지로 이동시키기
    # 코드가 없으면
    if code is None:
        raise HTTPException(status_code=421, detail="code is not found")
    # 단기 실행 토큰 발급
    short_token = insta.get_short_token(code)
    # 장기 실행 토큰 발급
    # {access_token: 'access_token', token_type: 'token_type', expires_in: 5184000}
    return insta.get_long_token(short_token)
