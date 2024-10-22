import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Response
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from werkzeug.utils import secure_filename
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_redis import RedisChatMessageHistory
import json

app = Flask(__name__)

# 환경 변수에서 SerpApi, Imgur, OpenAI 및 Naver API 키 로드
load_dotenv()
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# 지원되는 이미지 파일 형식 (Imgur에서 지원하는 파일 형식)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}

# 네이버 쇼핑 API 데이터 가져오기
def get_naver_shopping_data(query, display=5):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "sim"  # 항상 정확도순으로 정렬
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('items', [])

# 상품 정보 포맷팅
def format_product_info(items):
    formatted_items = []
    for item in items:
        link = f"https://search.shopping.naver.com/search/all?query={quote(item['title'])}"
        image_html = f"<img src='{item['image']}' alt='Product Image' style='max-width:100%; max-height:200px;'>"
        formatted_item = (
            f"상품명: {item['title']}\n"
            f"이미지: {image_html}\n"
            f"가격: {item['lprice']}원\n"
            f"브랜드: {item.get('brand', 'N/A')}\n"
            f"카테고리: {item.get('category1', '')}/{item.get('category2', '')}\n"
            f"링크: {link}\n"
        )
        formatted_items.append(formatted_item)
    return "\n".join(formatted_items)

# LLM 모델 초기화
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", streaming=True)

# 프롬프트 템플릿 설정
template = """
너는 '트렌드 네비게이터'라는 이름의 네이버 쇼핑 도우미야. 
사용자에게 최적의 쇼핑 정보를 제공하는 것이 너의 역할이야.

다음 규칙을 준수해:
1. 사용자가 요청한 상품과 관련 없는 상품은 절대 추천하지 마.
2. 항상 상품명, 이미지, 가격, 브랜드, 카테고리, 링크 정보를 **위에 정해진 형식**대로 제공해. 
   형식은 다음과 같아:
   
   - 상품명: 한성컴퓨터 TFG Cloud CF 3모드 듀얼 가스켓 기계식 키보드
   - 이미지: <img src='https://shopping-phinf.pstatic.net/main_4818931/48189314618.20240604091600.jpg' alt='Product Image' style='max-width:100%; max-height:200px;'>
   - 가격: 139000원
   - 브랜드: 한성컴퓨터
   - 카테고리: 디지털/가전/주변기기
   - 링크: https://search.shopping.naver.com/search/all?query=한성컴퓨터%20TFG%20Cloud%20CF%203모드%20듀얼%20가스켓%20기계식%20키보드

3. 만약 유효하지 않은 링크가 있다면 대체 링크를 제공하거나 검색 방법을 안내해.
4. 결과가 부족하거나 찾을 수 없는 경우, 솔직하게 '정보 부족'이라고 답해.
5. 동일한 상품 정보를 중복되지 않게 제공하고, 최신 정보를 유지해.

상품 정보:
{product_info}

대화 기록:
{history}

사용자: {human_input}
트렌드 네비게이터:
"""

# 프롬프트 생성
prompt = ChatPromptTemplate.from_template(template)

# 메모리 설정
memory = ConversationBufferMemory(memory_key="history", input_key="human_input")

# 파일 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Imgur에 이미지 업로드
def upload_image_to_imgur(image_path):
    print("이미지 Imgur 업로드 시도 중...")
    url = "https://api.imgur.com/3/upload"
    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        print("이미지 Imgur 업로드 성공")
        return response.json()['data']['link']  # 업로드된 이미지 URL 반환
    else:
        print(f"Imgur 업로드 실패: {response.status_code}, {response.text}")
        return None

# Google Lens API를 통해 이미지 검색
def search_with_google_lens(image_url):
    print(f"Google Lens를 통한 이미지 검색 시도 중... URL: {image_url}")
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_lens",  # Google Lens API 엔진
        "url": image_url,         # 검색할 이미지 URL
        "api_key": SERPAPI_KEY    # SerpApi API 키
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Google Lens 이미지 검색 성공")
        return response.json()  # 전체 JSON 결과 반환
    else:
        print(f"Google Lens 검색 실패: {response.status_code}, {response.text}")
        return None

@app.route('/')
def home():
    return render_template('chat.html')

# 채팅 요청 처리
@app.route('/chat', methods=['POST'])
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

# 이미지 업로드 및 Google Lens 분석 처리
@app.route('/upload', methods=['POST'])
def upload_image():
    print("이미지 업로드 요청 수신")
    if 'file' not in request.files:
        return jsonify({"error": "파일이 제공되지 않았습니다."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400

    # 파일 형식 확인
    if not allowed_file(file.filename):
        return jsonify({"error": "지원되지 않는 파일 형식입니다. PNG, JPG, JPEG, GIF, TIFF만 지원됩니다."}), 400

    try:
        filename = secure_filename(file.filename)
        image_path = os.path.join("uploads", filename)
        file.save(image_path)
        print(f"이미지 {filename} 저장 완료. 경로: {image_path}")

        # Imgur에 이미지 업로드 후 URL 가져오기
        image_url = upload_image_to_imgur(image_path)
        if not image_url:
            return jsonify({"error": "이미지 업로드에 실패했습니다."}), 500

        # Google Lens를 사용하여 이미지 검색
        search_result = search_with_google_lens(image_url)
        if not search_result:
            return jsonify({"error": "이미지에서 유사한 결과를 찾을 수 없습니다."}), 400

        # 'visual_matches'에서 'title'만 추출
        visual_matches = search_result.get('visual_matches', [])
        titles = [match.get('title') for match in visual_matches if 'title' in match]

        print(f"검색된 타이틀 목록: {titles}")

        # 첫 번째 타이틀만 반환
        if titles:
            first_title = titles[0]
            print(f"첫 번째 타이틀: {first_title}")

            # 이미지 타이틀을 질문으로 사용하여 LLM에 바로 전달
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

        else:
            return jsonify({"message": "이미지에서 적절한 타이틀을 찾을 수 없습니다."})

    except Exception as e:
        print(f"예외 발생: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)