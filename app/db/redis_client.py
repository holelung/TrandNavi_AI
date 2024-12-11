# app/db/redis_client.py
import redis
from flask import current_app

redis_jwt = None
redis_message = None

def init_redis():
    global redis_jwt
    global redis_message

    if not current_app:
        raise RuntimeError("Application context is not available.")

    redis_jwt = redis.from_url(current_app.config['REDIS_JWT_URL'], decode_responses=True)
    redis_message = redis.from_url(current_app.config['REDIS_MESSAGE_URL'], decode_responses=True)

def get_redis_jwt():
    if redis_jwt is None:
        raise RuntimeError("Redis JWT client is not initialized. Call init_redis() first.")
    return redis_jwt

def get_redis_message():
    if redis_message is None:
        raise RuntimeError("Redis Message client is not initialized. Call init_redis() first.")
    return redis_message

def get_recent_history(session_id, limit=5):
    """가장 최근의 N개의 대화 쌍을 반환"""
    history = redis_message.lrange(session_id, 0, -1)  # 전체 기록 가져오기
    return history[-(limit * 2):] if len(history) >= (limit * 2) else history

