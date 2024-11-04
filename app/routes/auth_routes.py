# app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.db import Session
from app.models.user_model import User
from app.db.redis_client import redis_client

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from datetime import timedelta
import redis

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    
    session = Session()
    new_user = User(name=name, email=email, password=password)
    session.add(new_user)
    session.commit()
    session.close()
    
    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 400


# protected endpoint
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# JWT 갱신 토큰 사용
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)


# 로그아웃
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    redis_client.setex(jti, timedelta(minutes=30),"true")
    return jsonify(message="Successfully logged out"),200