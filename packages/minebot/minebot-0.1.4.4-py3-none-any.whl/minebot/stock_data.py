import json
import requests

def getapi(file_id='1hrbd8YQuHBIiraTVZ74zG_MsqCphD-bw'):
    """
    Google Drive에서 공개된 JSON 파일을 다운로드하여 Python 딕셔너리로 반환합니다.

    Args:
        file_id (str): Google Drive 파일 ID

    Returns:
        dict: JSON 데이터
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    response.raise_for_status()
    return json.loads(response.text)
