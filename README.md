# Google Calendar API 

基于 FastAPI 的 Google Calendar API 服务。

## 配置步骤

1. 创建 Google Cloud Project
   - 访问 [Google Cloud Console](https://console.cloud.google.com)
   - 创建新项目
   - 启用 Google Calendar API 和 Tasks API

2. 配置 OAuth 2.0
   - 创建 OAuth 2.0 client ID (Desktop app)
   - 下载 credentials.json

3. 配置 GitHub Secrets
   - 添加 APP_NAME (应用名称)

4. 部署
   - 确保有可用的 self-hosted runner, 参考 [github_runner.md](./github_runner.md)
   - 推送代码到 main 分支触发部署

## 本地开发

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置凭证
   - 将 credentials.json 放在项目根目录

3. 运行服务
```bash
uvicorn app.main:app --port 8009 --reload
```
