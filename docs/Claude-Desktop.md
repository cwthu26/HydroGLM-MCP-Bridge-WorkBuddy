# Claude Desktop 接入

Claude Desktop 的本地 MCP 配置使用 `mcpServers` JSON。打开客户端提供的 Developer / Edit Config 入口，合并服务器配置后完全退出并重新启动客户端。[MCP 官方本地接入指南](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

本页针对本地 stdio 配置，未进行 Claude Desktop 桌面端实测。账号中的远程连接器需要远程 MCP 服务，本项目的 `server.py` 路径不能作为远程连接器 URL。

## 步骤

1. 安装 Python 3.10+，在项目目录配置密钥：`python3 configure_key.py --agent HydroGLM`。
2. 生成 JSON：

   ```bash
   python3 generate_config.py --client claude --output local.claude.mcp.json
   ```

   Windows 将 `python3` 换成 `py -3`。

3. 通过客户端设置打开本地 MCP 配置文件，将 `mcpServers.hydroglm_bridge` 合并到已有对象。官方指南列出的常见文件位置：

   - macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows：`%APPDATA%\Claude\claude_desktop_config.json`
   - Linux：`~/.config/Claude/claude_desktop_config.json`

   以实际版本中的配置编辑器为准。保留其他服务器设置。


4. 完全退出并重启 Claude Desktop，在本地工具列表确认 `ask_hydroglm`，之后直接问“水库汛限水位有什么作用？”。宿主按任务自动选用工具，日常无需点名；验证方法见 [连接验证与排障](使用说明.md#连接验证与排障)。

生成器不会给 Claude JSON 加入 Codex 专用的 `tool_timeout_sec`。API 侧等待上限是 600 秒；本地客户端是否允许这么长的工具请求，需按实际版本验证。移动项目目录、Python 环境或运行账户后，应重新生成配置并检查凭据可读性。
