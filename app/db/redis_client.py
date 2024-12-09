# app/db/redis_client.py

import redis
from flask import current_app

# JWT 토큰 관리용 Redis 클라이언트
redis_jwt = redis.from_url(current_app.config['REDIS_JWT_URL'], decode_responses=True)

# 메시지 저장용 Redis 클라이언트
redis_message = redis.from_url(current_app.config['REDIS_MESSAGE_URL'], decode_responses=True)
