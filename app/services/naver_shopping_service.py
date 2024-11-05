import os
import requests
import re
from urllib.parse import quote

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

def get_naver_shopping_data(query, display=5):
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

def format_product_info(items):
    formatted_items = []
    for item in items:
        # HTML 태그 제거
        title = re.sub(r'<.*?>', '', item['title'])  # 제목에서 HTML 태그 제거
        link = f"https://search.shopping.naver.com/search/all?query={quote(title)}"
        image_html = f"<img src='{item['image']}' alt='Product Image' style='max-width:100%; max-height:200px;'>"
        
        formatted_item = (
            f"상품명: {title}\n"
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