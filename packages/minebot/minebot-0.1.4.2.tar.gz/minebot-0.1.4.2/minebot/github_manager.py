import aiohttp
import asyncio
import json

async def get_github_file():
    url = "https://raw.githubusercontent.com/KoreanSniper/minebot/main/stock_history.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # 오류 발생 시 예외 처리
            # MIME 타입이 'text/plain'일 수 있기 때문에, 텍스트로 받았을 때 수동으로 JSON 파싱
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type or 'text/plain' in content_type:
                # JSON 데이터로 변환
                data = await response.text()  # 텍스트로 받음
                return json.loads(data)  # 수동으로 JSON으로 변환
            else:
                raise ValueError(f"Unexpected content type: {content_type}")
