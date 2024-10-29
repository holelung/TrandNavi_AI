from flask import Blueprint, jsonify, request, Response
from app.services.naver_shopping_service import get_naver_shopping_data, format_product_info
from app.llm_config import llm, memory, prompt
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # 네이버 쇼핑 API로 상품 정보 가져오기
    items = get_naver_shopping_data(user_message)
    product_info = format_product_info(items)
    
    # 대화 기록 가져오기
    history = memory.load_memory_variables({})["history"]
    
    # 프롬프트 생성
    messages = prompt.format_messages(
        product_info=product_info,
        history=history,
        human_input=user_message
    )
    
    def generate():
        full_response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield f"data: {json.dumps({'response': full_response})}\n\n"
        
        # 메모리 업데이트
        memory.save_context({"human_input": user_message}, {"output": full_response})
    
    return Response(generate(), content_type='text/event-stream')
