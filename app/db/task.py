# app/db/task.py

from celery import Celery
import json
from app.db import Session
from app.db.redis_client import redis_message as redis_client
from app.models import Message  # SQLAlchemy 세션 관리
from datetime import datetime

celery = Celery(__name__, broker='redis://localhost:6379/1', backend='redis://localhost:6379/1')

@celery.task
def sync_chat_messages(room_id):
    key = f"chat:room:{room_id}:messages"
    db = Session()  # 새로운 세션 생성

    try:
        while True:
            raw_msg = redis_client.lpop(key)
            if raw_msg is None:
                break
            msg_data = json.loads(raw_msg)

            # Message 객체 생성 및 DB 저장
            new_message = Message(
                room_id=room_id,
                user_id=msg_data["user_id"],
                content=msg_data["content"],
            )
            db.add(new_message)
        
        db.commit()  # 세션 커밋
    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        raise e
    finally:
        db.close()  # 세션 닫기
