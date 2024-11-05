from flask import Flask
from dotenv import load_dotenv
#from app.db import db
from app.models import *
from app.config import Config

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화 및 설정 함수
def create_app():
    app = Flask(__name__)
    
    #db.init_app(app)

    # 블루프린트 등록
    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app  # Flask 앱 객체 반환
