import os, requests, schemas

from dotenv import load_dotenv
from fastapi import HTTPException

# 환경변수 로드
load_dotenv()

# 인스타 로그인 및 프로필 정보 가져오기 및 유저 관련 API
app_id = os.getenv('INSTA_APP_ID')
secret_id = os.getenv('INSTA_APP_SECRET_ID')
redirect_url = "https://localhost:8000/api/v1/insta/redirection"
authorize_url = f"https://api.instagram.com/oauth/authorize?client_id=\
    {app_id}&redirect_uri={redirect_url}&scope=user_profile,user_media&response_type=code"
get_short_token_url = "https://api.instagram.com/oauth/access_token"
get_user_name_url = "https://graph.instagram.com/me?fields=username&access_token="
get_user_info_url = "https://i.instagram.com/api/v1/users/web_profile_info/?username="
get_long_token_url = f"https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret={secret_id}&access_token="
refresh_token_url = "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token="


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
        res = requests.post(get_short_token_url, headers = headers, data = data).json()
        # 유효하지 않은 코드면
        if 'error_type' in res:
            raise HTTPException(status_code=404, detail=res['error_message'])
            # 적절한 페이지로 이동시키기
        else: return res["access_token"]
    except Exception as ex:
        print(ex.args)


# 장기 토큰 얻기
def get_long_token(short_access_token: str):
    try:
        res = requests.get(get_long_token_url+short_access_token).json()
        return res
    except Exception as ex:
        print(ex.args)


def get_refresh_token(long_access_token: str):
    try:
        refresh_token = requests.get(refresh_token_url+long_access_token).json()
        return refresh_token
    except Exception as ex:
        return -1


# 엑세스 토큰으로 user info 반환
def get_user_info(access_token: str):
    try:
        # 엑세스 토큰을 통해 user 정보 받아오기에 필요한 username을 가져온다.
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
        
        insta_id = user_info['id']
        full_name = user_info['full_name']
        follower = user_info['edge_followed_by']['count']
        following = user_info['edge_follow']['count']
        profile_image_url = user_info['profile_pic_url']

        user_create_data = schemas.UserCreate(insta_id=insta_id, username=username,\
        full_name=full_name, follower=follower, following=following, \
            profile_image_url=profile_image_url)

        return user_create_data

    except Exception as ex:
        print(ex.args)