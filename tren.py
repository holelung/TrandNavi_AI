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
import json

app = Flask(__name__)

# 환경 변수에서 SerpApi, Imgur, OpenAI 및 Naver API 키 로드
load_dotenv()
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# 홈 페이지 라우트 추가
@app.route('/')
def home():
    return render_template('main.html')

# 네이버 쇼핑 API 데이터 가져오기
def get_naver_shopping_data(query, display=3):
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

# Google Images Results API로 특정 상품명을 검색해 첫 번째 이미지 URL 가져오기
def get_google_image_url(product_name):
    url = "https://serpapi.com/search.json"
    params = {
        "q": product_name,
        "tbm": "isch",  # 이미지 검색을 위한 설정
        "api_key": SERPAPI_KEY,
        "gl": "kr",    # 국가 코드 (예: 한국 'kr')
        "hl": "ko"     # 언어 코드 (예: 한국어 'ko')
    }

    # SerpAPI에 요청 보내기
    response = requests.get(url, params=params)
    
    # 요청 성공 시 첫 번째 이미지 URL 반환
    if response.status_code == 200:
        data = response.json()
        image_results = data.get("images_results", [])
        
        # 첫 번째 이미지 URL 가져오기
        if image_results:
            first_image_url = image_results[0].get("original")
            print(f"가져온 이미지 URL for '{product_name}':", first_image_url)  # 첫 번째 이미지 URL 출력
            return first_image_url  # 첫 번째 이미지의 URL 반환
    
    # 실패 시 None 반환
    return None

# 상품 정보 포맷팅
def format_product_info(items):
    formatted_items = []
    for item in items:
        # 각 상품명으로 이미지를 검색하여 URL 가져오기
        image_url = get_google_image_url(item['title'])
        image_html = f"<img src='{image_url}' alt='Product Image' style='max-width:100%; max-height:200px;'>"
        link = f"https://search.shopping.naver.com/search/all?query={quote(item['title'])}"
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
2. 항상 상품명, 이미지, 가격, 브랜드, 카테고리, 링크 정보를 **아래 정해진 형식**대로 제공해. 
   형식은 다음과 같아:
   
   - 상품명: [상품명]
   - 이미지: <img src='[이미지 URL]' alt='Product Image' style='max-width:100%; max-height:200px;'>
   - 가격: [가격]
   - 브랜드: [브랜드]
   - 카테고리: [카테고리]
   - 링크: [링크 텍스트](링크 URL)

3. 만약 유효하지 않은 링크가 있다면 대체 링크를 제공하거나 검색 방법을 안내해.
4. 결과가 부족하거나 찾을 수 없는 경우, 솔직하게 '정보 부족'이라고 답해.
5. 동일한 상품 정보를 중복되지 않게 제공하고, 최신 정보를 유지해.
   
사용자 요청을 토대로 위 형식을 적용해 정보를 제공해줘.

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

# 채팅 요청 처리
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']

    # 네이버 쇼핑 API로 상품 정보 가져오기 (3개의 추천 상품)
    items = get_naver_shopping_data(user_message, display=3)
    if not items:
        return jsonify({"error": "No products found"}), 404

    # 각 상품명에 맞는 이미지를 포함하여 상품 정보 포맷팅
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

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
