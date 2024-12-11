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
    db = Session()

    try:
        while True:
            raw_msg = redis_client.lpop(key)
            if raw_msg is None:
                print("Redis에서 가져올 메시지가 없습니다.")
                break

            try:
                msg_data = json.loads(raw_msg)
                print("Redis 메시지 디코딩 성공:", msg_data)
            except json.JSONDecodeError as e:
                print("JSON 디코딩 실패:", e)
                continue

            try:
                new_message = Message(
                    room_id=room_id,
                    user_id=msg_data["user_id"],
                    content=msg_data["content"],
                )
                db.add(new_message)
                print("DB 메시지 추가 성공:", new_message)
            except Exception as e:
                print("DB 메시지 추가 실패:", e)
                continue

        db.commit()
        print("DB 커밋 성공")
    except Exception as e:
        db.rollback()
        print("DB 작업 실패. 롤백 실행:", e)
    finally:
        db.close()
