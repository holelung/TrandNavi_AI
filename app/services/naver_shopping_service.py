import os
import requests
import re
from urllib.parse import quote

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

def get_naver_shopping_data(query, display=3):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "sim"
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


def get_price_comparison(query):
    items = get_naver_shopping_data(query, display=10)  # 가격 비교를 위해 더 많은 상품을 가져옴
    if not items:
        return "상품 정보를 찾을 수 없습니다."

    prices = [item['lprice'] for item in items]
    min_price = min(prices)
    max_price = max(prices)
    return min_price, max_price