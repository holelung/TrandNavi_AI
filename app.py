import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
import json

from langsmith import Client


# API 키 설정
load_dotenv()

LANGCHAIN_TRACING_V2 = True
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
client = Client()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

app = Flask(__name__)

# 네이버 쇼핑 API 데이터 가져오기 (LCEL로 변환)
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
            f"링크: {link}\n"
        )
        formatted_items.append(formatted_item)
    return "\n".join(formatted_items)

# LLM 모델 초기화
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o", streaming=True)

template = """
너는 '트렌드 네비게이터'라는 이름의 네이버 쇼핑 도우미야. 
사용자에게 최적의 쇼핑 정보를 제공하는 것이 너의 역할이야. 

다음 규칙을 준수해:
1. 사용자가 요청한 상품과 관련 없는 상품은 절대 추천하지 마.
2. 항상 상품명, 이미지, 가격, 브랜드, 카테고리, 링크 정보를 함께 제공해.
3. 만약 유효하지 않은 링크가 있다면 대체 링크를 제공하거나 검색 방법을 안내해.
4. 결과가 부족하거나 찾을 수 없는 경우, 솔직하게 '정보 부족'이라고 답해.

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
    history = memory.load_memory_variables({}).get("history", "")  # history가 없으면 빈 문자열로 처리

    # LCEL 체인을 사용하여 데이터 처리
    def generate():
        # 'RunnableParallel'은 병렬로 작업을 처리하므로, 여기서는 단순히 각 값을 전달하는 방식으로 구성합니다.
        retrieval = RunnableParallel({
            "human_input": RunnablePassthrough(),  # 사용자의 입력을 그대로 전달
            "history": RunnablePassthrough(),  # 대화 기록을 그대로 전달
            "product_info": RunnablePassthrough()  # 상품 정보를 그대로 전달
        })

        # Prompt 생성
        messages = prompt.format_messages(
            product_info=product_info,
            history=history,
            human_input=user_message
        )

        # LLM으로부터 스트리밍 응답 받기
        try:
            full_response = ""
            for chunk in llm.stream(messages):  # messages는 올바른 형식이어야 함
                if chunk.content:
                    full_response += chunk.content
                    yield f"data: {json.dumps({'response': full_response})}\n\n"
        finally:
            wait_for_all_tracers()
            
        # 메모리 업데이트
        memory.save_context({"human_input": user_message}, {"output": full_response})

    return Response(generate(), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)
