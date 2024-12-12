# app/routes/chat_routes.py
from flask import Blueprint, jsonify, request, Response, render_template
from datetime import datetime

from app.db.redis_client import redis_message
from app.db.redis_client import get_redis_message
from app.db.redis_client import get_recent_history 
from app.db.task import sync_chat_messages

from app.services.naver_shopping_service import get_naver_shopping_data
from app.services.naver_shopping_service import format_product_info
from app.services.naver_shopping_service import get_price_comparison 

from app.services.trend_service import get_related_topics  # 트렌드 서비스 추가

from app.db import Session
from app.models.chat_rooms_model import ChatRoom
from app.models.messages_model import Message

from app.llm_config import llm, prompt,price_comparison_prompt, trend_prompt, extract_keyword ,LLMConfig


from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity

import json 


chat_bp = Blueprint('chat', __name__)
llm_config = LLMConfig()

# 봇에게 받는 메시지
@chat_bp.route('/chat/createMessage', methods=['POST'])
def chat():
    verify_jwt_in_request()
    
    user_id = get_jwt_identity()    
    print(user_id)
    session_id = str(user_id)
    redis_conn = get_redis_message()

    # 유저가 입력한 메시지
    user_message = request.json['message']
    # 발급받은 채팅방 번호
    room_id = request.json['room_id']

    if room_id is None:
        return jsonify({"error": "room_id is required"}), 400

    def generate_response():
        
        
        if "트렌드" in user_message or "유행" in user_message:
            try:
                print("[DEBUG] 트렌드 요청 처리 시작")
                
                # 키워드 추출
                keyword = extract_keyword(user_message)
                if not keyword:
                    raise ValueError("키워드를 추출할 수 없습니다.")
                
                # 트렌드 데이터 가져오기
                trend_data = get_related_topics(keyword)
                if not trend_data:
                    raise ValueError("트렌드 데이터를 가져오는 데 실패했습니다.")
                
                # 트렌드 정보 구성
                rising_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['rising'])])
                top_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['top'])])
                trend_info = {
                    "keyword": keyword,
                    "rising_topics": rising_topics,
                    "top_topics": top_topics
                }
                
                # LLMConfig에 트렌드 정보 저장
                llm_config.set_trend_info(trend_info)
                print("[DEBUG] 트렌드 정보 저장 완료")
                print(f"[DEBUG] 저장된 트렌드 정보: {llm_config.get_trend_info()}")

                # LLM 프롬프트 생성
                print("[DEBUG] LLM 프롬프트 생성 시작")
                messages = trend_prompt.format_messages(
                    keyword=trend_info['keyword'],
                    rising_topics=trend_info['rising_topics'],
                    top_topics=trend_info['top_topics'],
                    history="\n".join(get_recent_history(session_id=session_id, limit=5)),
                    human_input=user_message
                )
                print("[DEBUG] LLM 프롬프트 생성 완료")

                # 응답 스트리밍
                full_response = ""
                for chunk in llm.stream(messages):
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'response': full_response}, ensure_ascii=False)}\n\n"

                # Redis 저장
                message_data = {
                    "room_id": room_id,
                    "user_id": "BotMessage",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                }
                redis_key = f"chat:room:{room_id}:messages"
                redis_conn.rpush(redis_key, json.dumps(message_data, ensure_ascii=False))
                print("[DEBUG] Redis에 트렌드 응답 저장 완료")

                return
            except Exception as e:
                error_message = f"트렌드 요청 처리 중 오류가 발생했습니다: {str(e)}"
                print(f"[DEBUG] {error_message}")
                # Redis 저장
                message_data = {
                    "room_id": room_id,
                    "user_id": "BotMessage",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }
                redis_key = f"chat:room:{room_id}:messages"
                redis_conn.rpush(redis_key, json.dumps(message_data, ensure_ascii=False))
                yield f"data: {json.dumps({'response': error_message}, ensure_ascii=False)}\n\n"
                return
        
        # 가격 비교 처리
        if "가격 비교" in user_message or "가격비교" in user_message:
            print("[DEBUG] 가격 비교 요청 처리 시작")
            
            # 가격 비교 정보 가져오기
            min_price, max_price = get_price_comparison(user_message)
            price_comparison_info = {
                "product_name": user_message,  # 사용자 요청 메시지를 상품 이름으로 간주
                "min_price": min_price,
                "max_price": max_price
            }
            
            # LLMConfig에 가격 비교 정보 저장
            llm_config.set_price_comparison_info(price_comparison_info)
            print("[DEBUG] 가격 비교 정보 저장 완료")
            print(f"[DEBUG] 저장된 가격 비교 정보: {llm_config.get_price_comparison_info()}")

            # LLM 프롬프트 생성
            print("[DEBUG] LLM 프롬프트 생성 시작")
            messages = price_comparison_prompt.format_messages(
                product_info=llm_config.get_product_info(),  # 기존 상품 정보
                price_comparison_info=llm_config.get_price_comparison_info(),  # 가격 비교 정보
                history="\n".join(get_recent_history(session_id=session_id, limit=5)),
                human_input=user_message
            )
            print("[DEBUG] LLM 프롬프트 생성 완료")

            # 응답 스트리밍
            full_response = ""
            for chunk in llm.stream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield f"data: {json.dumps({'response': full_response}, ensure_ascii=False)}\n\n"
            
            # Redis 저장
            message_data = {
                "room_id": room_id,
                "user_id": "BotMessage",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            }
            redis_key = f"chat:room:{room_id}:messages"
            redis_conn.rpush(redis_key, json.dumps(message_data, ensure_ascii=False))
            print("[DEBUG] Redis에 가격 비교 응답 저장 완료")

            return

 

        print("[DEBUG] 네이버 쇼핑 API 호출 시작")

        items = get_naver_shopping_data(user_message)
        if items:
            print(f"[DEBUG] 네이버 쇼핑 API 호출 성공 - {len(items)}개의 상품 반환")
            product_info = format_product_info(items)
            print("[DEBUG] 상품 정보 포맷 완료")
            print("[DEBUG] 최종 상품 포맷팅 정보:")
            print(product_info)  # 최종 포맷된 상품 정보 출력
            
            # LLMConfig에 product_info 저장
            llm_config.set_product_info(product_info)
            print("[DEBUG] llm_config에 전달된 상품 정보:")
            print(llm_config.get_product_info())  # LLMConfig에 저장된 데이터 출력
        else:
            print("[DEBUG] 네이버 쇼핑 API에서 상품 정보를 찾을 수 없음")
            product_info = "상품 정보를 찾을 수 없습니다."
            llm_config.set_product_info(product_info)
            print("[DEBUG] llm_config에 전달된 상품 정보:")
            print(llm_config.get_product_info())  

        # LLM 프롬프트 생성
        print("[DEBUG] LLM 프롬프트 생성 시작")
        messages = prompt.format_messages(
            product_info=llm_config.get_product_info(),  # LLMConfig에서 product_info 가져오기
            history="\n".join(get_recent_history(session_id=session_id, limit=5)),
            human_input=user_message
        )
        print("[DEBUG] LLM 프롬프트 생성 완료")


        # 응답 스트리밍
        full_response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield f"data: {json.dumps({'response': full_response}, ensure_ascii=False)}\n\n"

        user_message_data = {
            "room_id": room_id,
            "user_id": user_id,
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        }
        # Redis에 메시지 저장 (이전에는 redis_memory.save_context 사용)
        message_data = {
            "room_id": room_id,
            "user_id": "BotMessage",
            "content": full_response,
            "timestamp": datetime.now().isoformat()
        }
        redis_key = f"chat:room:{room_id}:messages"
        redis_conn.rpush(redis_key, json.dumps(user_message_data, ensure_ascii=False))  
        redis_conn.rpush(redis_key, json.dumps(message_data, ensure_ascii=False))
        
        print("[DEBUG] Redis에 응답 저장 완료")
        # sync_chat_messages.delay(room_id)


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
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    # 채팅방 존재 여부 확인
    session = Session()
    chat_room = session.query(ChatRoom).filter_by(room_id=room_id).first()
    session.close()

    if not chat_room:
        return jsonify({"error": "Chat room not found"}), 404

    # Redis에 메시지 임시 저장
    message_data = {
        "room_id": room_id,
        "user_id": user_id,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

    redis_conn = get_redis_message()  # redis_message 클라이언트 객체 얻기


    redis_key = f"chat:room:{room_id}:messages"
    redis_conn.rpush(redis_key, json.dumps(message_data, ensure_ascii=False))

    # 백그라운드로 동기화 태스크 전달
    # Celery를 이용한다면 다음과 같이 태스크 호출
    sync_chat_messages.delay(room_id)

    return jsonify({"message": "Message queued for syncing", "room_id": room_id}), 201

# 특정 채팅방의 메시지 기록 가져오기
@chat_bp.route('/chat/<int:room_id>/history', methods=['GET'])
@jwt_required()
def get_chat_history(room_id):
    # Redis 클라이언트 가져오기

    verify_jwt_in_request()

    user_id = get_jwt_identity()
    
    # Redis 키 설정
    redis_key = f"chat:room:{room_id}:messages"

    # Redis에서 메시지 가져오기
    try:
        raw_messages = redis_message.lrange(redis_key, 0, -1)  # 리스트의 모든 항목 가져오기
        if not raw_messages:
            return jsonify({"error": "No messages found in Redis"}), 404

        # JSON 형식으로 변환
        message_list = [
            json.loads(msg) for msg in raw_messages
        ]
        return jsonify(message_list), 200

    except Exception as e:
        print(f"Redis에서 메시지 로드 실패: {e}")
        return jsonify({"error": "Failed to load messages from Redis"}), 500

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


@chat_bp.route("/main/id:<chat_room_id>")
def chat_room(chat_room_id):
    # Redis에서 채팅 데이터 가져오기
    chat_data = redis_message.lrange(f"chat:room:{chat_room_id}:messages", 0, -1)  # Redis 리스트의 모든 데이터 가져오기
    
    messages = [json.loads(msg) for msg in chat_data]  # JSON 문자열을 파이썬 딕셔너리로 변환

    return render_template("chat_room.html", messages=messages, chat_room_id=chat_room_id)

@chat_bp.route("/main/id/<int:room_id>", methods=['POST'])
@jwt_required()
def start_chat(room_id):
    try:
        user_id = get_jwt_identity()
        session_id = str(user_id)

        # 클라이언트에서 전달된 데이터
        user_message = request.json.get('room_name')
        if not user_message:
            return jsonify({"error": "Invalid request. 'room_name' is required."}), 400

        # Redis 초기화 및 메시지 저장
        redis_conn = get_redis_message()
        redis_key = f"chat:room:{room_id}:messages"

        # 사용자 메시지 저장
        user_message_data = {
            "room_id": room_id,
            "user_id": user_id,
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        }
        redis_conn.rpush(redis_key, json.dumps(user_message_data))

        # LLM 메시지 생성 및 저장
        llm_response = f"LLM 응답: {user_message}방에 오신걸 환영합니다!"
        bot_message_data = {
            "room_id": room_id,
            "user_id": "BotMessage",
            "content": llm_response,
            "timestamp": datetime.now().isoformat(),
        }
        redis_conn.rpush(redis_key, json.dumps(bot_message_data))

        # Redis에서 저장된 메시지 로드
        messages = redis_conn.lrange(redis_key, 0, -1)
        message_list = [json.loads(msg) for msg in messages]

        print(f"[DEBUG] /main/id/<room_id> 라우트 호출 완료. 메시지 개수: {len(message_list)}")

        # 채팅방 HTML 렌더링
        return render_template("chat_room.html", room_id=room_id, messages=message_list)

    except Exception as e:
        print(f"[ERROR] /main/id/<room_id> 처리 중 오류 발생: {str(e)}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

