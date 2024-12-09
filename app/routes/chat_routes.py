# app/routes/chat_routes.py
from flask import Blueprint, jsonify, request, Response

from app.services.naver_shopping_service import get_naver_shopping_data
from app.services.naver_shopping_service import format_product_info
from app.services.naver_shopping_service import get_price_comparison

from app.services.trend_service import get_related_topics  # 트렌드 서비스 추가

from app.db import Session
from app.models.chat_rooms_model import ChatRoom
from app.models.messages_model import Message

from app.llm_config import llm, prompt, trend_template, extract_keyword  # 트렌드 템플릿 및 키워드 추출 함수 추가
from app.redis_handler import RedisChatMemory

from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity

import json 


chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/createMessage', methods=['POST'])
def chat():
    verify_jwt_in_request()
    
    user_message = request.json['message']
    session_id = request.json.get("session_id", "default_session")
    redis_memory = RedisChatMemory(session_id)

    def generate_response():
        # 트렌드 키워드가 있는지 확인
        if "트렌드" in user_message or "유행" in user_message:
            # 초기 대기 메시지 전송
            yield f"data: {json.dumps({'response': '트렌드 데이터를 가져오는 중입니다...'})}\n\n"
            
            # 키워드 추출
            keyword = extract_keyword(user_message)

            if keyword:
                trend_data = get_related_topics(keyword)

                if trend_data:
                    # 트렌드 템플릿에 데이터 포맷팅
                    rising_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['rising'])])
                    top_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['top'])])
                    
                    messages = trend_template.format(
                        keyword=keyword,
                        rising_topics=rising_topics,
                        top_topics=top_topics,
                        history="\n".join(redis_memory.get_recent_history(limit=5)),
                        human_input=user_message
                    )

                    # LLM에게 템플릿을 기반으로 응답 요청
                    response = ""
                    for chunk in llm.stream(messages):
                        if chunk.content:
                            response += chunk.content
                            yield f"data: {json.dumps({'response': response})}\n\n"

                    # Redis에 트렌드 요청 기록 저장
                    redis_memory.save_context(user_message, response)
                    return

                else:
                    # 트렌드 데이터 요청 실패 시
                    error_message = "트렌드 정보를 가져오는 데 실패했습니다."
                    redis_memory.save_context(user_message, error_message)
                    yield f"data: {json.dumps({'response': error_message})}\n\n"
                    return
        
        # 가격 비교 요청 처리
        if "가격 비교" in user_message:
            min_price, max_price = get_price_comparison(user_message)
            price_comparison_response = f"최저가: {min_price}원, 최고가: {max_price}원"
            redis_memory.save_context(user_message, price_comparison_response)
            yield f"data: {json.dumps({'response': price_comparison_response})}\n\n"
            return

        # 네이버 쇼핑 API로 상품 정보 가져오기
        items = get_naver_shopping_data(user_message)
        if items:
            product_info = format_product_info(items)
        else:
            product_info = "상품 정보를 찾을 수 없습니다."

        # 최근 대화 기록 불러오기
        recent_history = redis_memory.get_recent_history(limit=5)

        # 프롬프트 생성
        messages = prompt.format_messages(
            product_info=product_info,
            history="\n".join(recent_history),
            human_input=user_message
        )

        # 일반 응답 스트리밍
        full_response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield f"data: {json.dumps({'response': full_response}, ensure_ascii=False)}\n\n"


        # Redis에 채팅 기록 업데이트
        redis_memory.save_context(user_message, full_response)

    return Response(generate_response(), content_type='text/event-stream')


# 새 채팅방 생성
@chat_bp.route('/chat/createRoom', methods=['POST'])
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
@chat_bp.route('/chat/<int:room_id>/message', methods=['POST'])
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
@chat_bp.route('/chat/<int:room_id>/history', methods=['GET'])
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
@chat_bp.route('/chat/rooms', methods=['GET'])
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
@chat_bp.route('/chat/<int:room_id>', methods=['DELETE'])
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
