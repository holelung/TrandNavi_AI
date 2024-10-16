import os
import requests
from flask import Flask, render_template, request, Response
from urllib.parse import quote
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain.callbacks import StreamingStdOutCallbackHandler
from PIL import Image
import json
import io
import base64

app = Flask(__name__)

# API 키 설정
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')


# 네이버 쇼핑 API 데이터 가져오기
def get_naver_shopping_data(query, display=30):
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

def validate_and_process_link(item):
    original_link = item['link']
    
    # 네이버 검색 결과 페이지 링크 생성
    search_query = quote(item['title'])
    alternative_link = f"https://search.shopping.naver.com/search/all?query={search_query}"
    return alternative_link

# 상품 정보 포맷팅
def format_product_info(items):
    formatted_items = []
    for item in items:
        link = validate_and_process_link(item)
         # 항상 이미지 태그로 포맷팅
        image_html = f"<img src='{item['image']}' alt='Product Image' style='max-width:100%; max-height:200px;'>"
        formatted_item = (
            f"상품명: {item['title']}\n"
            f"이미지: {image_html}\n"
            f"가격: {item['lprice']}원\n"
            f"브랜드: {item.get('brand', 'N/A')}\n"
            f"카테고리: {item.get('category1', '')}/{item.get('category2', '')}\n"
            #f"링크: {link}\n"
        )
        formatted_items.append(formatted_item)
    return "\n".join(formatted_items)

# 커스텀 스트리밍 콜백 핸들러
class CustomStreamingCallbackHandler(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        print(token, end="", flush=True)

# LLM 모델 초기화
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o", streaming=True)


template = """
너는 '트렌드 네비게이터'라는 이름의 네이버 쇼핑 도우미야. 
사용자에게 최적의 쇼핑 정보를 제공하는 것이 너의 역할이야.


다음 규칙을 준수해:
1. 사용자가 요청한 상품과 관련 없는 상품은 절대 추천하지 마.
2. 항상 상품명, 이미지, 가격, 브랜드, 카테고리, 링크 정보를 **위에 정해진 형식**대로 제공해. 
   형식은 다음과 같아:
   
   - 상품명: 한성컴퓨터 TFG Cloud CF 3모드 듀얼 가스켓 기계식 키보드
   - 이미지: <img src='https://shopping-phinf.pstatic.net/main_4818931/48189314618.20240604091600.jpg' alt='Product Image' style='max-width:100%; max-height:200px;'>  이미지를 크롤링으로 가져옴
   - 가격: 139000원
   - 브랜드: 한성컴퓨터
   - 카테고리: 디지털/가전/주변기기
   - 링크: https://search.shopping.naver.com/search/all?query=한성컴퓨터%20TFG%20Cloud%20CF%203모드%20듀얼%20가스켓%20기계식%20키보드 상품명을 뒤에 넣는 식으로 강제함

3. 사용자의 상품에 대한 질문이 대해서 상품의 상품명, 카테고리, 가격이 포함되어 있지 않으면 해당 정보를 추가로 요구하는 질문을 반드시 해줘.
4. 이미지는 항상 상품명과 관련된 이미지만을 보여줘.
5. 동일한 상품 정보를 중복되지 않게 제공하고, 최신 정보를 유지해.


상품 정보:
{product_info}

대화 기록:
{history}

사용자: {human_input}
트렌드 네비게이터:
"""

prompt = ChatPromptTemplate.from_template(template)

# 메모리 설정
memory = ConversationBufferMemory(memory_key="history", input_key="human_input")

@app.route('/')
def home():
    return render_template('chat.html')
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

if __name__ == '__main__':
    app.run(debug=True) 