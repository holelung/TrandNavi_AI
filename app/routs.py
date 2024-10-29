from flask import Blueprint, jsonify, request
from .models import User
from . import db

main = Blueprint('main', __name__)

@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])

@main.route('/add_user', methods=['POST'])
def add_user():
    name = request.json.get('name')
    email = request.json.get('email')
    
    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User added successfully!"}), 201
