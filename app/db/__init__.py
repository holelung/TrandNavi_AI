# app/db/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.models.base import Base

# 데이터베이스 엔진 생성
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)

# 세션 팩토리 생성
Session = sessionmaker(engine)

# 테이블 생성 (필요 시)
Base.metadata.create_all(engine)
