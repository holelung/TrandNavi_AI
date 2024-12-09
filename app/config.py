import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    REDIS_JWT_URL = os.getenv("REDIS_JWT_URL")
    REDIS_MESSAGE_URL = os.getenv("REDIS_MESSAGE_URL")
    
    print(SQLALCHEMY_DATABASE_URI)