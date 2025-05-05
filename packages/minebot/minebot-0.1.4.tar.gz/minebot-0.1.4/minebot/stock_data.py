from .github_manager import fetch_github_data

def getapi():
    """ 
    minebot의 주식 데이터를 반환하는 함수입니다.
    """
    return fetch_github_data()  # 비동기 방식으로 데이터를 가져옴
