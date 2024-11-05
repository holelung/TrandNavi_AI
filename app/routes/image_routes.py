from flask import Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename
from app.utils.helpers import allowed_file
from app.services.imgur_service import upload_image_to_imgur
from app.services.google_lens_service import search_with_google_lens
from app.services.naver_shopping_service import get_naver_shopping_data, format_product_info
from app.llm_config import llm, image_prompt, get_image_llm_with_redis_memory
import json
import os

image_bp = Blueprint('image', __name__)

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    print("이미지 업로드 요청을 수신했습니다.")

    # 'uploads' 폴더가 없다면 생성
    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"'{upload_folder}' 디렉터리가 생성되었습니다.")

    # 파일이 업로드되지 않았을 경우의 오류 처리
    if 'file' not in request.files:
        return jsonify({"error": "파일이 제공되지 않았습니다."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "지원되지 않는 파일 형식입니다."}), 400

    try:
        # 이미지 저장
        filename = secure_filename(file.filename)
        image_path = os.path.join(upload_folder, filename)
        file.save(image_path)
        print(f"이미지 파일이 저장되었습니다: {image_path}")

        # Imgur에 업로드
        image_url = upload_image_to_imgur(image_path)
        if not image_url:
            return jsonify({"error": "이미지 업로드에 실패했습니다."}), 500

        # Google Lens API로 타이틀 추출
        search_result = search_with_google_lens(image_url)
        if not search_result:
            return jsonify({"error": "이미지에서 유사한 결과를 찾을 수 없습니다."}), 400

        visual_matches = search_result.get('visual_matches', [])
        if not visual_matches:
            print("오류: 시각적 일치 항목이 없습니다.")
            return jsonify({"error": "이미지에서 관련된 항목을 찾을 수 없습니다."}), 400

        # 타이틀 추출 및 기본값 설정
        first_match_title = visual_matches[0].get('title', "관련 항목을 찾을 수 없음")
        print(f"추출된 타이틀: {first_match_title}")

        # Redis 메모리 사용 준비
        session_id = request.form.get("session_id", "default_session")
        respond_to_user = get_image_llm_with_redis_memory(session_id)

        # 이미지 기반 질문 템플릿 사용
        response_text = respond_to_user(first_match_title, first_match_title)

        def generate():
            yield f"data: {json.dumps({'response': response_text})}\n\n"
            print("질문이 성공적으로 생성되었습니다.")

        return Response(generate(), content_type='text/event-stream')

    except Exception as e:
        print(f"예외 발생: {str(e)}")
        return jsonify({"error": str(e)}), 500
