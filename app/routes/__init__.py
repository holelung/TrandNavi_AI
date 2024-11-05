# app/routes/__init__.py
from .chat_routes import chat_bp
from .image_routes import image_bp
from .main_routes import main_bp  # 기본 경로 라우트 추가
from .auth_routes import auth_bp
from .cart_routes import cart_bp

blueprints = [
    chat_bp,
    image_bp,
    main_bp,
    auth_bp,
    cart_bp,
]
