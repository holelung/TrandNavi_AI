from flask import Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename
from app.utils.helpers import allowed_file
from app.services.imgur_service import upload_image_to_imgur
from app.services.google_lens_service import search_with_google_lens
from app.services.naver_shopping_service import get_naver_shopping_data, format_product_info
from app.llm_config import llm, memory, prompt  # 여기서 llm, memory, prompt를 app.llm_config에서 불러옴
import json

image_bp = Blueprint('image', __name__)

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 제공되지 않았습니다."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "지원되지 않는 파일 형식입니다."}), 400
    
    try:
        filename = secure_filename(file.filename)
        image_path = f"uploads/{filename}"
        file.save(image_path)
        
        image_url = upload_image_to_imgur(image_path)
        if not image_url:
            return jsonify({"error": "이미지 업로드에 실패했습니다."}), 500

        search_result = search_with_google_lens(image_url)
        if not search_result:
            return jsonify({"error": "이미지에서 유사한 결과를 찾을 수 없습니다."}), 400
        
        visual_matches = search_result.get('visual_matches', [])
        titles = [match.get('title') for match in visual_matches if 'title' in match]
        
        if titles:
            first_title = titles[0]
            items = get_naver_shopping_data(first_title)
            product_info = format_product_info(items)
            
            history = memory.load_memory_variables({})["history"]
            messages = prompt.format_messages(
                product_info=product_info,
                history=history,
                human_input=first_title
            )
            
            def generate():
                full_response = ""
                for chunk in llm.stream(messages):
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'response': full_response})}\n\n"
                memory.save_context({"human_input": first_title}, {"output": full_response})
            
            return Response(generate(), content_type='text/event-stream')
        
        return jsonify({"message": "이미지에서 적절한 타이틀을 찾을 수 없습니다."})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
