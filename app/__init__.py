# app/__init__.py
from flask import Flask
from app.config import Config
from app.db import engine  # 생성된 engine 사용
from app.models import Base  # Base 임포트

# Flask 앱 초기화 및 설정 함수
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # config 설정 불러오기

    # 데이터베이스 테이블 생성
    Base.metadata.create_all(engine)  # 엔진을 사용해 테이블 생성

    # 블루프린트 등록
    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app  # Flask 앱 객체 반환
