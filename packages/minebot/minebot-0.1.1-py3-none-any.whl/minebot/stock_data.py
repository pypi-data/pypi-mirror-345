from .github_manager import get_github_file


def getapi():
    """ 
    minebot의 주식 데이터를 반환하는 함수입니다.
    """
    return get_github_file()