import os
import requests

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_related_topics(keyword):
    if not SERPAPI_KEY:
        print("오류: SERPAPI_KEY 환경 변수가 설정되지 않았습니다.")
        return None

    params = {
        "engine": "google_trends",
        "q": keyword,
        "data_type": "RELATED_TOPICS",
        "api_key": SERPAPI_KEY
    }
    
    url = "https://serpapi.com/search.json"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json()
        print("API 호출 성공, 데이터 처리 중...")

        related_topics = results.get("related_topics", {})
        rising_topics = related_topics.get("rising", [])
        top_topics = related_topics.get("top", [])

        # 상위 3개 주제 정렬
        sorted_rising_topics = sorted(
            rising_topics, 
            key=lambda x: int(x["value"]), 
            reverse=True
        )[:3]
        
        sorted_top_topics = sorted(
            top_topics, 
            key=lambda x: int(x["value"]), 
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

        print("데이터 처리 완료, 상위 3개의 주제 반환 중...")
        return topics_data
    else:
        print(f"오류: Google Trends API 호출 실패, 상태 코드: {response.status_code}")
        print("응답 내용:", response.text)
        return None
