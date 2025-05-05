import requests
import base64

def get_github_file():
    url = "https://raw.githubusercontent.com/KoreanSniper/minebot/main/stock_history.json"
    response = requests.get(url)
    response.raise_for_status()  # 오류 발생 시 예외 처리
    return response.json()