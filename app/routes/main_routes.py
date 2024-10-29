# app/routes/main_routes.py

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('chat.html')  # chat.html 템플릿 파일을 사용할 경우
