import os
import requests

SERPAPI_KEY = os.getenv('SERPAPI_KEY')

def search_with_google_lens(image_url):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None
