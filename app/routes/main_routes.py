# app/routes/main_routes.py

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
from flask import request

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')  # chat.html 템플릿 파일을 사용할 경우

@main_bp.route('/login')
def login():
    return render_template('login.html')  

@main_bp.route('/register')
def register():
    return render_template('register.html')

@main_bp.route('/cart') 
@jwt_required()
def cart():
    return render_template('cart.html')

@main_bp.route('/main')
def main():
    return render_template('main.html')