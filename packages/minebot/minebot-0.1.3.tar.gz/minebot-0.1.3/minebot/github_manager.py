import aiohttp
import asyncio
import json

async def get_github_file():
    url = "https://raw.githubusercontent.com/KoreanSniper/minebot/main/stock_history.json"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # 오류 발생 시 예외 처리
            return await response.json()

# 비동기 함수 실행을 위한 별도 함수
def fetch_github_data():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_github_file())
