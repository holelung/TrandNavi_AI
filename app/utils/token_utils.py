# app/utils/token_utils.py
from app.db.redis_client import redis_client

def is_token_blacklisted(jti):
    return bool(redis_client.get(jti))