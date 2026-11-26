# 密钥与数据

`ask_hydroglm` 会把 `question`、可选的会话编号和模式参数发送至 `https://hanhai-ai.com`，并使用用户配置的瀚海 API Key 认证。MCP 服务不会自行扫描或上传项目文件。若宿主 AI 把本地内容放入 `question`，这些内容也会被发送。

密钥读取顺序为环境变量优先，其次为个人配置文件：

- `HANHAI_HYDROGLM_API_KEY`
- `HANHAI_HYDROGLM_PLUS_API_KEY`
- `${XDG_CONFIG_HOME}/hydroglm-mcp/credentials.json`；未设置 `XDG_CONFIG_HOME` 时为 `~/.config/hydroglm-mcp/credentials.json`。

以上位置与旧版兼容，两个版本可共用凭据。Linux/macOS 保存器设置目录权限 0700、文件权限 0600；Windows 使用当前用户目录，访问权限由 Windows ACL 管理，脚本不声称 POSIX 权限位能提供同等保护。

不要将真实密钥、完整个人客户端配置、内部业务资料加入公开仓库。示例使用个人凭据文件，不嵌入密钥。`.gitignore` 包含常见密钥和本机生成文件名，但仍应在提交前查看实际暂存文件。

服务不执行上游返回的代码。专业结论、公式与数值由宿主侧独立验证。默认诊断不打印密钥；向他人提供错误信息时优先保留 HTTP 状态码、时间与请求 ID。
