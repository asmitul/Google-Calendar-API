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

## 认证设置

1. 从 Google Cloud Console 下载 OAuth 2.0 客户端凭据文件，并将其重命名为 `credentials.json` 放在 `app/data/` 目录下。

2. 首次运行时，程序会提供一个 URL。请复制该 URL 并在浏览器中打开。

3. 完成 Google 授权后，您会获得一个授权码。将该授权码复制并粘贴回终端。

4. 认证完成后，凭据会被保存在 `app/data/token.pickle` 文件中，后续请求将自动使用该凭据。
