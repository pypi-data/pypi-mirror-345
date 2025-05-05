import time
import requests

def get_github_file():
    timestamp = int(time.time())  # 매 요청마다 달라지는 파라미터
    url = f"https://raw.githubusercontent.com/KoreanSniper/minebot/main/stock_history.json?ts={timestamp}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
