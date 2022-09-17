from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import schemas, crud, insta
from database import get_db

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


# A-3
# access_token으로 유저 정보 업데이트, 없다면 생성 후 user를 반환한다.
# 토큰 발급 및 리프레쉬 후 호출
# 또는 링크 생성 시 user 정보 업데이트를 위해 호출
# 프론트에서는 나중에 user 정보 조회를 위해 user_id 로컬에 저장하기
@router.post("/by_access_token")
def user_info_change_by_access_token(access_token: str, db: Session = Depends(get_db)):
    # 엑세스 토큰으로 user 정보 가져옴
    user_info = insta.get_user_info(access_token=access_token)

    # user 업데이트 시도, 성공시 user반환, 실패시 insta_id_not_found 반환
    res = update_user(user=user_info, db=db)

    # user 업데이트 실패시 user 생성
    if res == 'insta_id_not_found':
        return create_user(user=user_info, db=db)
    else:
        return res


# A-4
# user 생성에 필요한 정보를 보내면 user를 생성한다.
@router.post('/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user=user)


# A-5
# user 업데이트에 필요한 정보를 보내면 user 정보를 업데이트한다.
@router.put('/', response_model=schemas.User)
def update_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.update_user(db, user=user)


# A-6
# user_id를 path variable로 받아서 해당 user의 정보를 반환한다.
@router.get('/{user_id}', response_model=schemas.User)
def show_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id=user_id)


# A-7
# user_id를 path variable로 받아서 해당 유저를 soft delete한다.
@router.delete('/{user_id}', status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db=db, user_id=user_id)


# B-8
# 질문 공유를 위한 url을 생성
@router.get('/url', response_model=str)
def get_question_url(user_id: int, question_id: int, db: Session = Depends(get_db)):
    insta_id = crud.get_user(db, user_id=user_id).insta_id
    return f'http://localhost:3000/{insta_id}/{question_id}'
