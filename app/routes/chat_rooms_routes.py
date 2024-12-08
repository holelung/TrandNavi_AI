from flask import Blueprint, request, jsonify
from app.db import Session
from app.models.chat_rooms_model import ChatRoom
from app.models.messages_model import Message
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

chat_rooms_bp = Blueprint('chat_rooms', __name__)

# 새 채팅방 생성
@chat_rooms_bp.route('/chat', methods=['POST'])
@jwt_required()
def create_chat_room():
    verify_jwt_in_request()

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    room_name = data.get('room_name', f"Chat Room by User {user_id}")

    session = Session()
    new_chat_room = ChatRoom(room_name=room_name)
    session.add(new_chat_room)
    session.commit()
    room_id = new_chat_room.room_id
    session.close()

    return jsonify({"message": "Chat room created", "room_id": room_id, "room_name": room_name}), 201


# 특정 채팅방에 메시지 저장
@chat_rooms_bp.route('/chat/<int:room_id>/message', methods=['POST'])
@jwt_required()
def add_message_to_room(room_id):
    verify_jwt_in_request()

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    session = Session()
    chat_room = session.query(ChatRoom).filter_by(room_id=room_id).first()

    if not chat_room:
        session.close()
        return jsonify({"error": "Chat room not found"}), 404

    new_message = Message(room_id=room_id, user_id=user_id, content=content)
    session.add(new_message)
    session.commit()
    session.close()

    return jsonify({"message": "Message added to chat room", "message_id": new_message.message_id}), 201


# 특정 채팅방의 메시지 기록 가져오기
@chat_rooms_bp.route('/chat/<int:room_id>/history', methods=['GET'])
@jwt_required()
def get_chat_history(room_id):
    verify_jwt_in_request()

    user_id = get_jwt_identity()
    session = Session()

    # 채팅방 존재 여부 확인
    chat_room = session.query(ChatRoom).filter_by(room_id=room_id).first()
    if not chat_room:
        session.close()
        return jsonify({"error": "Chat room not found"}), 404

    messages = session.query(Message).filter_by(room_id=room_id).order_by(Message.created_at).all()
    session.close()

    # 메시지를 JSON 형태로 변환
    message_list = [
        {
            "message_id": msg.message_id,
            "user_id": msg.user_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]
    return jsonify(message_list), 200


# 모든 채팅방 목록 불러오기
@chat_rooms_bp.route('/chat/rooms', methods=['GET'])
@jwt_required()
def get_chat_rooms():
    verify_jwt_in_request()

    user_id = get_jwt_identity()
    session = Session()

    # 모든 채팅방 조회
    chat_rooms = session.query(ChatRoom).order_by(ChatRoom.created_at).all()
    session.close()

    # JSON 변환
    chat_rooms_list = [
        {
            "room_id": room.room_id,
            "room_name": room.room_name,
            "created_at": room.created_at.isoformat()
        }
        for room in chat_rooms
    ]
    return jsonify(chat_rooms_list), 200


# 특정 채팅방 삭제
@chat_rooms_bp.route('/chat/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_chat_room(room_id):
    verify_jwt_in_request()

    user_id = get_jwt_identity()
    session = Session()

    chat_room = session.query(ChatRoom).filter_by(room_id=room_id).first()
    if not chat_room:
        session.close()
        return jsonify({"error": "Chat room not found"}), 404

    session.delete(chat_room)
    session.commit()
    session.close()

    return jsonify({"message": "Chat room deleted successfully"}), 200
