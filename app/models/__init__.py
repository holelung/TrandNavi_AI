# app/models/__init__.py
from app.models.user_model import User
from app.models.base import Base

# 모델들을 여기서 import하여 인식시킴
__all__ = ["User", "Base"]
