# database.py
# database 연결과 관련된 파일

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv



import os

# 환경변수 로드
load_dotenv()

# DB 주소
DB_URL = (f"mysql+pymysql://{os.getenv('MYSQL_USER')}" +
          f":{os.getenv('MYSQL_ROOT_PASSWORD')}@{os.getenv('MYSQL_HOST')}" +
          f":{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8")


# sqlalchemy 엔진, main.py에서 사용
engine = create_engine(DB_URL, encoding = 'utf8')

# 데이터베이스 세션클래스, 이를 이용해 생성한 인스턴스로 DB에 접근해서 CRUD가능
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB모델이나 클래스를 만들기 위해 선언한 클래스(후에 상속해서 사용)
Base = declarative_base()
