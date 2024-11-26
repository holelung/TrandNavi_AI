import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 DATABASE_URI 정보 가져오기
DATABASE_URI = os.getenv("DATABASE_URI")

# pymysql을 통해 MySQL 연결
try:
    # pymysql.connect()는 connection string을 직접 받지 않으므로 정보 추출 필요
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="8427",
        database="llm",
        port=3306
    )
    print("MySQL 연결 성공!")
    connection.close()
except Exception as e:
    print("MySQL 연결 실패:", e)

from sqlalchemy import create_engine

# SQLAlchemy 엔진 생성 및 연결 테스트
DATABASE_URI = "mysql+pymysql://root:8427@localhost:3306/llm"
engine = create_engine(DATABASE_URI)

try:
    with engine.connect() as connection:
        print("SQLAlchemy로 MySQL 연결 성공!")
except Exception as e:
    print("SQLAlchemy로 MySQL 연결 실패:", e)