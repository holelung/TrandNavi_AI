from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.redis_handler import RedisChatMemory
from app.services.trend_service import get_related_topics
#테스트
# LLM 모델 초기화
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", streaming=True)

# 템플릿 설정
template = """
    너는 '트렌드 네비게이터'라는 이름의 네이버 쇼핑 도우미야.
    사용자가 요청한 상품과 관련된 정보를 충분히 얻기 위해 필요한 세 가지 질문을 번호 형식으로 자동 생성하고,
    질문이 충분히 충족되면 최적의 상품 추천을 제공해줘.
    
    질문을 생성할 때 항상 질문 앞에 "1번", "2번", "3번"과 같이 번호를 붙여 제공해.
    
    예시:
    - 사용자가 "새로운 컴퓨터를 찾고 있어요"라고 하면:
        "새로운 컴퓨터를 찾으시는군요, 좋은 제품을 추천해 드리기 위해 몇 가지 질문을 드리겠습니다.
        
        1번. 어떤 용도로 컴퓨터를 사용하실 계획인가요? (예: 게임, 그래픽 작업 등)
        2번. 데스크탑과 노트북 중 어떤 종류의 컴퓨터를 찾고 계신가요?
        3번. 예상하시는 가격대는 어떻게 되나요?"
        
    충분한 정보가 수집되면 상품 추천을 아래 형식대로 제공해줘:
    - 상품명: [상품명]
    - 이미지: <img src='[이미지 URL]' alt='Product Image' style='max-width:100%; max-height:200px;'>
    - 가격: [가격]원
    - 브랜드: [브랜드]
    - 카테고리: [카테고리]
    - 링크: [링크]
    
    추천한 후, 사용자에게 다음과 같은 질문으로 "가격 비교가 필요하신가요?"라고 묻고,
    사용자가 "네"라고 대답하면 "몇 번 상품의 가격 비교가 필요하신가요?"라고 질문해줘.
    
    사용자가 몇 번 상품의 가격 비교를 요청하면, 해당 상품의 최저가와 최고가를 가격 비교 API를 통해 가져와서 제공해줘.
    위 데이터를 바탕으로 다음과 같이 응답해줘:
    1. 현재 가격 비교한 상품의 최저가 최고가를 비교해 2문장으로 설명  
    2. 사용자에게 도움될 만한 구체적인 가격비교 결론 제공

    

    대화 기록:
    {history}

    사용자: {human_input}
    트렌드 네비게이터:
"""

# Image-based template
image_template = """
    너는 '트렌드 네비게이터'라는 이름의 네이버 쇼핑 도우미야. 이미지를 인식하여 관련 상품 정보를 제공해줘.
    인식된 **'{title}'**에 따라 필요한 정보를 얻기 위해 세 가지 질문을 자동으로 생성해줘.
    
    질문 앞에 "1번", "2번", "3번"을 붙여 제공해.
    
    예시:
    - 인식된 타이틀이 컴퓨터 관련일 때:
        "**'{title}'**을 찾으시는군요. 좋은 제품을 추천하기 위해 몇 가지 질문을 드리겠습니다.
        
        1번. 어떤 용도로 사용하실 계획인가요? (예: 게임, 그래픽 작업 등)
        2번. 노트북과 데스크탑 중 어떤 종류를 찾고 계신가요?
        3번. 예상하시는 가격대는 어떻게 되나요?"
        
    충분한 정보가 수집되면 상품 추천을 아래 형식대로 제공해줘:
    - 상품명: [상품명]
    - 이미지: <img src='[이미지 URL]' alt='Product Image' style='max-width:100%; max-height:200px;'>
    - 가격: [가격]원
    - 브랜드: [브랜드]
    - 카테고리: [카테고리]
    - 링크: [링크]

    대화 기록:
    {history}
    
    사용자: {human_input}
    트렌드 네비게이터:
"""

keyword_extract_template = """
다음 사용자의 메시지에서 검색이나 트렌드 분석에 사용할 핵심 키워드 하나만 추출해주세요.
키워드는 명사 형태로 추출하고, 다른 설명 없이 키워드만 반환해주세요.

예시:
입력: "요즘 캠핑 트렌드가 어떤지 궁금해요"
출력: 캠핑

입력: "최근 유행하는 신발 브랜드 추천해주세요"
출력: 신발

입력: {message}
출력:"""



trend_template = """
너는 '트렌드 네비게이터'라는 이름의 쇼핑 트렌드 분석가야.
현재 '{keyword}' 관련 트렌드 데이터를 기반으로 분석과 추천을 제공할 거야.

제공된 트렌드 데이터:
[상승 트렌드]
{rising_topics}

[인기 트렌드]
{top_topics}

위 데이터를 바탕으로 다음과 같이 응답해줘:
1. 현재 '{keyword}' 분야의 전반적인 트렌드 동향을 2-3문장으로 설명
2. 가장 주목할 만한 상승 트렌드 2개와 그 이유 설명
3. 사용자에게 도움될 만한 구체적인 제품 카테고리나 스타일 추천

이전 대화 기록:
{history}

사용자 메시지: {human_input}
트렌드 네비게이터:
"""



# ChatPromptTemplate 초기화
prompt = ChatPromptTemplate.from_template(template)
image_prompt = ChatPromptTemplate.from_template(image_template)
trend_prompt = ChatPromptTemplate.from_template(trend_template)
# 키워드 추출 프롬프트 템플릿
keyword_prompt = ChatPromptTemplate.from_template(keyword_extract_template)

# Redis 기반 텍스트 메모리 설정 함수
def get_llm_with_redis_memory(session_id):
    """Redis 기반의 텍스트 LLM 메모리 설정"""
    redis_memory = RedisChatMemory(session_id)

    def respond_to_user(user_input):
        redis_memory.add_message(f"User: {user_input}")
        history = redis_memory.get_recent_history(limit=5)  # 최근 5개 메시지 가져오기

        messages = prompt.format_messages(
            product_info="",  # 네이버 API 호출로 받은 상품 정보를 여기에 추가 가능
            history="\n".join(history),  # 최근 대화 기록
            human_input=user_input
        )

        response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                response += chunk.content
        
        redis_memory.add_message(f"LLM: {response}")
        return response

    return respond_to_user

# Redis 기반 이미지 메모리 설정 함수
def get_image_llm_with_redis_memory(session_id):
    """Redis 기반의 이미지 LLM 메모리 설정"""
    redis_memory = RedisChatMemory(session_id)

    def respond_to_user(user_input, title):
        redis_memory.add_message(f"User: {user_input}")
        history = redis_memory.get_recent_history(limit=2)  # 최근 5개 메시지 가져오기

        messages = image_prompt.format_messages(
            title=title,
            history="\n".join(history),  # 최근 대화 기록
            human_input=user_input
        )

        response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                response += chunk.content
        
        redis_memory.add_message(f"LLM: {response}")
        return response

    return respond_to_user

# Redis 기반 트렌드 메모리 설정 함수
def get_trend_llm_with_redis_memory(session_id):
    """Redis 기반의 트렌드 LLM 메모리 설정"""
    redis_memory = RedisChatMemory(session_id)

    def respond_to_user(keyword):
        redis_memory.add_message(f"User: {keyword}")
        history = redis_memory.get_recent_history(limit=2)  # 최근 5개 메시지 가져오기

        # Trend 데이터 가져오기
        trend_data = get_related_topics(keyword)
        rising_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['rising'])])
        top_topics = "\n".join([f"{i+1}. {topic['title']} ({topic['value']})" for i, topic in enumerate(trend_data['top'])])

        messages = trend_prompt.format_messages(
            keyword=keyword,
            rising_topics=rising_topics,  # 상승 주제 채워넣기
            top_topics=top_topics,         # 인기 주제 채워넣기
            history="\n".join(history),     # 최근 대화 기록
            human_input=keyword
        )

        response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                response += chunk.content
        
        redis_memory.add_message(f"LLM: {response}")
        return response

    return respond_to_user

def extract_keyword(message: str) -> str:
    """사용자 메시지에서 핵심 키워드를 추출"""
    messages = keyword_prompt.format_messages(message=message)
    response = llm.invoke(messages)  # streaming=False로 한 번에 받기
    
    # 응답에서 불필요한 공백과 개행 제거
    keyword = response.content.strip()
    
    # 키워드가 없거나 너무 긴 경우 예외 처리
    if not keyword or len(keyword.split()) > 2:
        raise ValueError("유효하지 않은 키워드입니다.")
        
    return keyword
