import os
import requests

IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')

def upload_image_to_imgur(image_path):
    url = "https://api.imgur.com/3/upload"
    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()['data']['link']
    else:
        return None
