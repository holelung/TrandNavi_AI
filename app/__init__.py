
# app/__init__.py
from flask import Flask, jsonify
from app.config import Config
from app.db import engine  # 생성된 engine 사용
from app.models import Base  # Base 임포트
from flask_jwt_extended import JWTManager
from app.db.redis_client import redis_client
from app.utils.token_utils import is_token_blacklisted


# Flask 앱 초기화 및 설정 함수
def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)  # config 설정 불러오기
    
    # jwt 설정 
    jwt = JWTManager(app)
    
    # 인증 오류 콜백 함수 설정
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({
            'message': 'Missing Authorization Header'
        }), 401
    
    # 블랙리스트 검증 로직 추가
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return is_token_blacklisted(jti)    
    
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(engine)  # 엔진을 사용해 테이블 생성


    # 블루프린트 등록
    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app  # Flask 앱 객체 반환
