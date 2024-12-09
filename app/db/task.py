# app/db/task.py

from celery import Celery
import json
from app.db import redis_client
from app.models import Message, db  # SQLAlchemy 세션 관리
from datetime import datetime

celery = Celery(__name__, broker='redis://localhost:6379/1', backend='redis://localhost:6379/1')

@celery.task
def sync_chat_messages(room_id):
    key = f"chat:room:{room_id}:messages"
    # 모든 메시지를 LRANGE로 가져온 후 처리할 수도 있고
    # 혹은 LPOP을 반복하면서 없을 때까지 처리할 수도 있음
    
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
        db.session.add(new_message)
    
    db.session.commit()
