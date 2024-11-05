from serpapi import GoogleSearch
import json
import os

# SerpAPI API 키 설정
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_related_topics(keyword):
    print(f"검색어 '{keyword}'에 대해 관련 주제 요청 중...")  # 진행 상황 프린트
    params = {
        "engine": "google_trends",
        "q": keyword,
        "data_type": "RELATED_TOPICS",
        "api_key": SERPAPI_KEY
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    print("API 요청 성공, 데이터 처리 중...")  # API 요청 성공 프린트

    # 관련 주제 데이터 추출
    related_topics = results.get("related_topics", {})
    rising_topics = related_topics.get("rising", [])
    top_topics = related_topics.get("top", [])
    
    # rising과 top 주제 각각에서 value가 높은 상위 3개 항목 선택
    sorted_rising_topics = sorted(
        rising_topics, 
        key=lambda x: int(x["extracted_value"]), 
        reverse=True
    )[:3]
    
    sorted_top_topics = sorted(
        top_topics, 
        key=lambda x: int(x["extracted_value"]), 
        reverse=True
    )[:3]

    topics_data = {
        "rising": [
            {
                "title": topic["topic"]["title"],
                "type": topic["topic"]["type"],
                "value": topic["value"],
                "link": topic["link"]
            }
            for topic in sorted_rising_topics
        ],
        "top": [
            {
                "title": topic["topic"]["title"],
                "type": topic["topic"]["type"],
                "value": topic["value"],
                "link": topic["link"]
            }
            for topic in sorted_top_topics
        ]
    }
    
    print("데이터 처리 완료, 상위 3개의 주제 반환 중...")  # 데이터 처리 완료 프린트
    return topics_data

# 실행 예시
if __name__ == "__main__":
    keyword = "카고 팬츠"
    print(f"'{keyword}'에 대한 관련 주제 데이터 수집 시작...")
    related_topics_data = get_related_topics(keyword)
    print("최종 상위 3개 관련 주제 결과:")
    print(json.dumps(related_topics_data, ensure_ascii=False, indent=4))
