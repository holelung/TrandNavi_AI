import os
import requests
import json

# SerpAPI API 키 설정
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def safe_int(value):
    """값을 안전하게 int로 변환"""
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"[DEBUG] 값 변환 실패: {value}")
        return None
    

def get_related_topics(keyword):
    """키워드에 대한 관련 주제 트렌드를 수집하여 상위 주제를 반환"""
    if not SERPAPI_KEY:
        print("오류: SERPAPI_KEY 환경 변수가 설정되지 않았습니다.")
        return None
    else:
        print(f"API 키가 확인되었습니다: {SERPAPI_KEY[:4]}****")  # 키 일부만 표시하여 보안 유지

    # API 요청 준비
    params = {
        "engine": "google_trends",
        "q": keyword,
        "data_type": "RELATED_TOPICS",
        "api_key": SERPAPI_KEY
    }
    
    url = "https://serpapi.com/search.json"

    try:
        print(f"'{keyword}'에 대해 Google Trends 관련 주제 요청 중...")  # 진행 상황 출력
        response = requests.get(url, params=params)

        # 응답 상태 코드 확인
        if response.status_code == 200:
            results = response.json()
            print("Google Trends API 호출 성공, 데이터 처리 중...")  # API 호출 성공
            
            # API 응답 데이터 출력
            print("API 응답 데이터:", json.dumps(results, ensure_ascii=False, indent=4))

            # 관련 주제 데이터 추출
            related_topics = results.get("related_topics", {})
            rising_topics = related_topics.get("rising", [])
            top_topics = related_topics.get("top", [])

            sorted_rising_topics = [
                {"title": topic["topic"]["title"], "value": safe_int(topic["value"]), "link": topic["link"]}
                for topic in rising_topics
                if safe_int(topic["value"]) is not None
            ]
            sorted_rising_topics = sorted(sorted_rising_topics, key=lambda x: x["value"], reverse=True)[:3]

            sorted_top_topics = [
                {"title": topic["topic"]["title"], "value": safe_int(topic["value"]), "link": topic["link"]}
                for topic in top_topics
                if safe_int(topic["value"]) is not None
            ]
            sorted_top_topics = sorted(sorted_top_topics, key=lambda x: x["value"], reverse=True)[:3]

            # 데이터가 없을 경우 처리
            if not sorted_rising_topics and not sorted_top_topics:
                print("오류: 상승 또는 인기 주제가 없습니다.")
                return None  # 또는 적절한 오류 메시지를 반환

            # 결과 데이터 포맷팅
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
            print("상위 3개 상승 주제:", [topic['title'] for topic in topics_data['rising']])
            print("상위 3개 인기 주제:", [topic['title'] for topic in topics_data['top']])
            return topics_data
        else:
            print(f"오류: Google Trends API 호출 실패, 상태 코드: {response.status_code}")
            print("응답 내용:", response.text)  # 오류 응답 내용 출력
            return None

    except requests.exceptions.RequestException as e:
        print(f"Google Trends API 호출 중 예외 발생: {e}")  # 예외 발생 로그
        return None
