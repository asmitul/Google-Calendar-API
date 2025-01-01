import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks']
# 修改凭据文件的路径
TOKEN_PATH = 'app/data/token.pickle'
CREDENTIALS_PATH = 'app/data/credentials.json'

async def get_credentials():
    creds = None
    
    # 尝试从文件加载已存在的凭据
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # 如果没有凭据或凭据已失效
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            # 使用 run_console 替代 run_local_server
            creds = flow.run_console()
            
        # 保存凭据以供下次使用
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return creds 