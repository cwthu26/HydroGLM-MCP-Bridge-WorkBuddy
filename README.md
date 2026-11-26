# HydroGLM MCP Bridge

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/) [![MCP](https://img.shields.io/badge/MCP-stdio-informational)](https://modelcontextprotocol.io/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

npm 包名：`hydroglm-mcp-bridge` · 版本：`1.0.1` · npm 入口需要 Node.js 22+ 和 Python 3.10+。

**Connect HydroGLM to your AI assistant through MCP.**

HydroGLM MCP Bridge 将 **HydroGLM / HydroGLM-plus** 封装为 MCP 工具，让 DeepSeek Harness、Codex、WorkBuddy、Claude Desktop 等支持本地 MCP 的 AI 客户端，在处理水文、水资源、水库调度及水电任务时调用专业大模型。

> **工作方式：**客户端通过 `ask_hydroglm` 获取 HydroGLM 的专业建议，再由客户端自身的工具读取文件、运行 Python 或生成成果。HydroGLM API 不会直接操作本地文件。

## Features

- **专业模型调用**：通过 `ask_hydroglm` 咨询 HydroGLM 或 HydroGLM-plus。
- **多客户端接入**：提供 DeepSeek Harness 一键安装，以及 Codex、WorkBuddy、Claude Desktop 和通用 stdio MCP 配置示例。
- **按任务选用**：工具描述包含水利专业任务的选用提示；是否自动调用取决于宿主客户端。
- **轻量部署**：仅需 Python 3.10+，无需额外安装 Python 依赖。
- **独立密钥管理**：支持一次性保存模型 API Key，不必在 MCP 配置中明文填写。

## npm / npx 使用

先安装 Node.js 22+ 和 Python 3.10+。npm 包提供启动入口并保留原 Python 服务，不会自动安装 Python。以下命令在包发布到 npm 后可用。

### 1. 保存密钥，只需一次

```bash
npx -y hydroglm-mcp-bridge@1.0.1 configure --agent HydroGLM
```

使用 plus 时将 `HydroGLM` 换成 `HydroGLM-plus`。已有本项目的个人凭据可继续使用。

### 2. 生成客户端配置

选择一条：

```bash
npx -y hydroglm-mcp-bridge@1.0.1 config --client codex --output local.codex.mcp.toml
npx -y hydroglm-mcp-bridge@1.0.1 config --client workbuddy --output local.workbuddy.mcp.json
npx -y hydroglm-mcp-bridge@1.0.1 config --client claude --output local.claude.mcp.json
```

将生成的片段合并到客户端设置后重载。npm 配置使用固定版本的 `npx` 命令，不使用临时缓存中的 `server.py` 路径。例如：

```json
{
  "mcpServers": {
    "hydroglm_bridge": {
      "command": "npx",
      "args": ["-y", "hydroglm-mcp-bridge@1.0.1"]
    }
  }
}
```

在客户端中直接提问，例如“水库汛限水位有什么作用？”，宿主按相关专业任务自动选用工具。

直接运行 `npx -y hydroglm-mcp-bridge@1.0.1` 会启动 stdio 服务并等待客户端输入，这是正常行为。若 Python 不在默认路径，可通过 `HYDROGLM_PYTHON` 指定 Python 可执行文件的完整路径。

发布者操作见 [npm 发布说明](docs/npm发布.md)，源码方式见下文。

## Quick Start｜Python 源码接入

### 1. Requirements

- Python **3.10+**
- HydroGLM 或 HydroGLM-plus 对应的瀚海 API Key
- 支持运行**本地 stdio MCP** 的客户端

下载并解压本项目，在项目根目录打开终端。Windows 下可将以下命令中的 `python3` 换为 `py -3`。

### 2. Configure API Key

```bash
python3 configure_key.py --agent HydroGLM
```

如果使用 HydroGLM-plus：

```bash
python3 configure_key.py --agent HydroGLM-plus
```

按提示输入密钥；输入过程不会在终端显示。每个模型只需设置一次。

### 3. Install in Your MCP Client

**DeepSeek Harness**

```bash
python3 install_hydroglm_dsh.py
python3 verify_hydroglm_dsh.py
```

默认配置桌面版的 `desktop` profile。Web 版在两条命令末尾加 `--profile web`。安装会注册 MCP 并安装咨询技能，具体步骤及直接聊天模型接入见 [DeepSeek Harness 接入指南](docs/DeepSeek-Harness.md)。

按使用的客户端生成配置片段：

**Codex**

```bash
python3 generate_config.py --client codex --output local.codex.mcp.toml
```

**WorkBuddy**

```bash
python3 generate_config.py --client workbuddy --output local.workbuddy.mcp.json
```

**Claude Desktop**

```bash
python3 generate_config.py --client claude --output local.claude.mcp.json
```

将生成的配置**合并到客户端现有的 MCP 配置**，保存并重载/重启客户端。生成器不会自动修改客户端设置。具体操作：

| Client | Setup Guide |
| --- | --- |
| DeepSeek Harness | [接入与验证](docs/DeepSeek-Harness.md) |
| Codex | [docs/Codex.md](docs/Codex.md) |
| WorkBuddy | [MCP 配置示例](examples/workbuddy.mcp.json) |
| Claude Desktop | [docs/Claude-Desktop.md](docs/Claude-Desktop.md) |
| 其他 stdio 客户端 | [examples/generic.mcp.json](examples/generic.mcp.json) |

配置生成器会写入本机 Python 和 `server.py` 的**绝对路径**；若移动项目目录，需重新生成。WorkBuddy、Claude Desktop 的配置格式已有示例，具体运行兼容性应在所用客户端验证。

## Usage｜使用示例

安装并启用后，确认客户端工具列表中出现 **`ask_hydroglm`**（DSH 中为 `mcp__hydroglm__ask_hydroglm`），即可直接提问：

> 水库汛限水位有什么作用？

> 请分析 Muskingum 河道汇流模型的适用条件，再用 Python 实现一个计算示例并检查水量平衡。

智能体可按任务决定是否调用 `ask_hydroglm` 获取专业建议，再使用客户端自身工具完成计算、文件处理等操作。通过客户端工具执行记录确认是否实际调用。

## When to Use｜何时调用

Codex、WorkBuddy 等客户端可以根据任务内容选择 `ask_hydroglm`，不要求每次指定工具名称。以下为建议场景：

| 任务场景 | 建议用法 |
| --- | --- |
| 解释降雨径流、水文预报、河道洪水演算等专业问题 | 考虑调用 HydroGLM 获取专业分析 |
| 分析水库调度规则、梯级水电运行约束和方案合理性 | 考虑调用 HydroGLM 辅助判断 |
| 比较 HBV、SWAT、Muskingum 等模型的原理、适用条件或参数 | 考虑调用 HydroGLM 获取专业建议 |
| 编写水文计算、入库流量预测或水库调度程序 | 需要专业方法判断时咨询 HydroGLM；代码编写和运行由宿主工具完成 |
| 读取 CSV、制作 Excel/PPT、修改普通 Python 代码 | 一般直接使用宿主工具，不必调用 HydroGLM |
| 普通聊天、翻译、无关领域问题 | 一般不调用 HydroGLM |

**自动调用规则：** `server.py` 的工具描述包含适用领域和调用建议。是否实际调用仍由宿主模型、客户端配置及权限决定，**不保证每次相关提问都会自动调用**。

**指定调用：** 如需明确使用 HydroGLM，可直接说“请调用 `ask_hydroglm` 分析这个问题”。若需要提高自动选择的概率，可参考 [按任务选用建议](docs/按任务选用建议.md) 配置客户端指令。

## MCP Tool

本项目目前提供 **1 个工具**：`ask_hydroglm`。

| Parameter | Required | Description |
| --- | --- | --- |
| `question` | Yes | 发送给 HydroGLM 的问题（最多 20,000 字符） |
| `agent` | No | `HydroGLM`（默认）或 `HydroGLM-plus` |
| `session_id` | No | 使用上次返回的会话编号继续追问（非负整数） |
| `web_search` | No | 请求启用/关闭上游联网搜索 |
| `enable_thinking` | No | 请求启用/关闭上游思考模式 |

**返回值：**文字回答，可能包含 `session_id`。不直接返回已执行的程序、计算结果或本地文件。

## How It Works

```text
用户提出水利专业任务
        ↓
DeepSeek Harness / Codex / WorkBuddy / Claude Desktop 等宿主智能体
        ↓  选择调用 ask_hydroglm
HydroGLM MCP Bridge（本地 stdio）
        ↓  HTTPS 请求
HydroGLM / HydroGLM-plus API
        ↓  返回专业回答
宿主智能体继续分析、计算、处理文件或编写报告
```

- MCP 桥接器使用的上游问答接口：`https://hanhai-ai.com/api/v1/agent/agent/openai/chat/completions`。
- 此地址是 **HTTP API**，不是可直接填入客户端的远程 MCP 地址。
- 本项目提供的是**本地 stdio MCP 服务**，并未提供 HTTP/SSE MCP 网关。

## Troubleshooting

| Problem | Check |
| --- | --- |
| 找不到 `ask_hydroglm` | 确认客户端支持本地 stdio，检查 Python/脚本绝对路径并重新加载 |
| 工具存在但没有自动调用 | 查看调用记录；宿主 AI 是否选择工具由客户端决定 |
| 缺少密钥 | 在运行 MCP 的同一系统用户下重新执行 `configure_key.py` |
| HTTP 401 / 403 | 确认密钥有效，且与 `agent` 对应 |
| HTTP 429 / 5xx / 超时 | 检查上游限制或服务状态；记录请求时间和可用的请求 ID |

检查密钥及模型列表：

```bash
python3 diagnose.py --agent HydroGLM
```

发起一次实际问答测试（会消耗 API 调用）：

```bash
python3 probe_chat.py --agent HydroGLM
```

更完整的排查见 [使用说明](docs/使用说明.md)。服务端 API 请求等待上限为 **600 秒**；Codex 示例工具超时为 **660 秒**，其他客户端的实际超时限制可能不同。

## Security

- API Key 存储在当前用户的个人配置目录中，也可通过环境变量提供；**不要提交密钥到 GitHub**。
- `question` 中的内容会发送到瀚海 API。未经授权，不要向工具传入保密资料或敏感的本地文件内容。
- 本工具仅提供专业文本咨询，不执行来自模型的代码；重要公式与计算结果应由宿主独立校验。

详见 [SECURITY.md](SECURITY.md)。

## Documentation

- [完整使用说明](docs/使用说明.md)
- [MCP 原理与调用场景](docs/MCP原理与调用场景.md)
- [按任务选用建议](docs/按任务选用建议.md)
- [版本与兼容性](docs/版本与兼容.md)
- [npm 发布说明](docs/npm发布.md)
- [更新记录](CHANGELOG.md) · [发布说明](RELEASE_NOTES.md)

## License

本项目基于 [MIT License](LICENSE) 发布，源自 [HydroGLM-Codex-MCP](https://github.com/LIMING-gloria/HydroGLM-Codex-MCP)。
