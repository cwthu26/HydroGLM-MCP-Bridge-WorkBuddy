# Codex 接入

Codex 的 MCP 配置使用 `config.toml` 中的 `[mcp_servers.<名称>]`。本版使用 `hydroglm_bridge`，与旧版 `hydroglm` 区分。`tool_timeout_sec` 表示单次工具调用超时。[OpenAI 官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

## 步骤

1. 在项目目录保存密钥：

   ```bash
   python3 configure_key.py --agent HydroGLM
   ```

2. 生成 TOML：

   ```bash
   python3 generate_config.py --client codex --output local.codex.mcp.toml
   ```

3. 将生成的新服务器表合并进 `~/.codex/config.toml`。设置了 `CODEX_HOME` 时，使用该目录中的 `config.toml`。原有 `[mcp_servers.hydroglm]` 可以保留。
4. 重新加载 MCP 或重启 Codex，确认新的服务器下出现 `ask_hydroglm`，之后直接提问，例如“水库汛限水位有什么作用？”。

生成结果中包含：

```toml
enabled = true
startup_timeout_sec = 20
tool_timeout_sec = 660
```

配置生成器不自动注册服务器，也不改写个人配置。它默认使用当前 Python 和本目录 `server.py` 的绝对路径。Windows 用 `py -3` 运行生成器即可生成本机路径。

旧版 `setup.sh`、`register_mcp.py` 及自动策略安装器仍留在原项目，已有用户继续使用原流程。通用版提供 [按任务选用建议](按任务选用建议.md)，可根据需要放入自己的指令文件；不会自动安装全局规则。

日常无需指定工具名。Codex 按任务自动选用 HydroGLM；可通过真实工具记录确认调用。工具连接验证和未自动调用时的排查见 [连接验证与排障](使用说明.md#连接验证与排障)。MCP 作用和选用条件见 [MCP 原理与调用场景](MCP原理与调用场景.md)。

配置说明核对日期：2026-11-20。这里针对可运行本地 stdio 的 Codex 环境；云端或网页环境不因存在本机 TOML 就自动获得本机 Python 进程访问能力。
