import asyncio
from .github_manager import get_github_file

# getapi()를 비동기 함수로 수정
async def getapi():
    """ 
    minebot의 주식 데이터를 반환하는 비동기 함수입니다.
    """
    return await get_github_file()  # 비동기 방식으로 데이터를 가져옴
