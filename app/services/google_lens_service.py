import os
import requests

SERPAPI_KEY = os.getenv('SERPAPI_KEY')

def search_with_google_lens(image_url):
    # API 키 확인
    if not SERPAPI_KEY:
        print("오류: SERPAPI_KEY 환경 변수가 설정되지 않았습니다.")
        return None
    else:
        print(f"API 키가 확인되었습니다: {SERPAPI_KEY[:4]}****")  # 키의 일부만 표시하여 보안 유지

    # API 요청 준비
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY
    }

    try:
        print("Google Lens API 호출 중...")  # API 호출 준비 로그
        response = requests.get(url, params=params)

        # 응답 상태 코드 확인
        if response.status_code == 200:
            print("Google Lens API 호출 성공")
            result = response.json()
            print("Google Lens API 응답:", result)  # API 응답 데이터 출력
            return result
        else:
            print(f"오류: Google Lens API 호출 실패, 상태 코드: {response.status_code}")
            print("응답 내용:", response.text)  # 오류 응답 내용 출력
            return None

    except requests.exceptions.RequestException as e:
        print(f"Google Lens API 호출 중 예외 발생: {e}")  # 예외 발생 로그
        return None
