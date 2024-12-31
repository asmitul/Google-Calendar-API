import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from ..config import SCOPES

async def get_credentials(force_refresh: bool = False) -> Credentials:
    """获取 Google OAuth 凭证"""
    creds = None
    
    # 尝试从文件加载
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 在生产环境中使用环境变量
            if os.getenv("GOOGLE_CLIENT_CONFIG"):
                client_config = json.loads(os.getenv("GOOGLE_CLIENT_CONFIG"))
            else:
                # 本地开发环境使用文件
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
        
        # 保存凭证
        if os.getenv("SAVE_CREDENTIALS", "false").lower() == "true":
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    return creds 