# HydroGLM-MCP-Bridge v1.0.1

发布日期：2026-11-20。

## 本版用途

通过本地 stdio MCP，将 HydroGLM / HydroGLM-plus 的水利专业咨询能力接入支持本地 MCP 的 AI 客户端。宿主 AI 可按任务需要咨询专业模型，并继续使用自己的工具完成文件处理、编程、计算和绘图。

## 本次整理

- 以 README 调整版为基础，新增 npm/npx 入口、跨平台 Python 查找及固定版本客户端配置生成；仍需 Python 3.10+。
- npm 发布名为 `hydroglm-mcp-bridge`，源码和 npm 版本均为 `1.0.1`。
- 重写首页，说明项目用途、适用任务和快速接入步骤。
- 新增《MCP 原理与调用场景》，解释 MCP、调用流程、选用条件、实际调用验证和能力边界。
- 补充使用说明、按任务选用建议及发布指南。
- 日常示例统一为直接提问、按任务自动选用，显式指定工具仅用于连接验证与排障。
- 密钥仍为首次保存、后续自动读取；不随源码分发。
- 明确支持的初始化协议版本，避免将未知协议版本原样回传为支持版本。
- 诊断时间改用固定北京时间偏移，避免 Windows 缺少 IANA 时区数据库时无法启动。
- 提供源码打包脚本和发布检查。

## 接入

需要 Python 3.10+，无需 pip 安装。首次运行 `python3 configure_key.py --agent HydroGLM` 保存密钥，再用 `generate_config.py` 为对应客户端生成片段。

完整步骤见 [README](README.md) 和 [使用说明](docs/使用说明.md)。Windows 将 `python3` 换成 `py -3`。

## 验证与兼容

发布整理包含本地离线测试、stdio 子进程检查、配置生成及源码包检查。GitHub Actions 提供 Linux、Windows、macOS 测试矩阵，实际状态以推送后的运行记录为准；本版不声称已经完成 WorkBuddy 或 Claude Desktop 的 GUI 实测。

旧版 HydroGLM-Codex-MCP 继续独立使用，凭据格式及 `ask_hydroglm` 工具参数兼容。本版不自动改写旧配置或安装全局调用规则。

本项目为源码分发，不等于已上架客户端连接器市场，也不提供远程 HTTP/SSE MCP 服务。
