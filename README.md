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

1. 从 Google Cloud Console 下载 OAuth 2.0 客户端凭据文件，并将其重命名为 `credentials.json` 放在 `data/` 目录下。

2. 确保在 Google Cloud Console 中添加以下授权重定向 URI：
   ```
   http://localhost:8088/
   ```

3. 首次运行服务器时，需要完成一次性的认证流程：
   - 服务器会启动一个本地认证服务器在端口 8088
   - 在本地浏览器中访问：http://your-server-ip:8088
   - 完成 Google 授权流程
   - 认证成功后，凭据会自动保存到 `app/data/token.pickle`

4. 后续请求将自动使用保存的凭据，除非凭据过期需要重新认证。

注意：
- 确保服务器的 8088 端口可访问
- 确保 app/data 目录存在且有正确的读写权限
- 首次认证后，正常的 API 请求将使用 8009 端口
