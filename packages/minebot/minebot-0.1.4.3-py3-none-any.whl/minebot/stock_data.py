import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow

# 구글 드라이브에서 stock_history.json을 불러오는 함수
def getapi():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    FILE_ID = '1pPcv20-B1VwT_DGVoUj95yJckfURnG-y'  # 실제 파일 ID

    # 인증 및 서비스 객체 생성
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)

    # 파일 다운로드
    request = service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    # JSON 변환
    fh.seek(0)
    data = json.load(fh)
    return data
