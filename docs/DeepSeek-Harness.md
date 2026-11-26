# 在 DeepSeek Harness 中使用 HydroGLM

DeepSeek Harness（DSH）可以通过 MCP 咨询 HydroGLM，也可以把 HydroGLM 添加到聊天模型列表。需要读写文件、运行代码或绘图时，保留 DeepSeek 作为主模型，使用 MCP 获取水利专业建议。只做专业问答时，也可以直接选择 HydroGLM 聊天模型。

## 1. 安装 MCP 工具

准备 Python 3.10 或更高版本、已安装的 DSH，以及瀚海平台签发的 HydroGLM API Key。将本仓库克隆或将源码 ZIP 解压到准备长期保留的位置，在项目根目录运行以下命令。Windows 下可将 `python3` 换为 `py -3`。

```bash
python3 configure_key.py --agent HydroGLM
python3 install_hydroglm_dsh.py
python3 verify_hydroglm_dsh.py
```

同一用户下已经配置 Bridge 密钥时，可以跳过第一条。密钥通过隐藏输入保存在用户配置目录中，也可由 DSH 进程继承环境变量 `HANHAI_HYDROGLM_API_KEY`。使用 HydroGLM-plus 时，配置和自检命令均加上或改用 `--agent HydroGLM-plus`，工具调用时也要指定该智能体。

安装与自检默认使用 `desktop` profile。用 Web 版或自定义 profile 时，两条命令都应指定对应名称，例如：

```bash
python3 install_hydroglm_dsh.py --profile web
python3 verify_hydroglm_dsh.py --profile web
```

脚本也读取 `DSH_PROFILE` 和 `DSH_HOME` 环境变量，可用 `--profile` 和 `--dsh-home` 覆盖。

安装器把 stdio MCP 注册写入 `~/.dsh/profiles/<profile>/cordis.patch.yml`（或指定的 DSH 数据目录），并将咨询技能复制到 DSH 用户技能目录 `skills/hydroglm-consult/`。它会备份有改动的现有文件。Bridge 通过 MCP 初始化信息提供咨询规则，咨询技能说明什么时候调用、怎么提问和如何核验。用户原有的 `personaSuffix` 可以继续使用。

## 2. 验证与排障

完全退出并重启 DSH，打开刚才配置的 profile 和一个新会话。先确认工具列表有 `mcp__hydroglm__ask_hydroglm`，再发一条实际请求：

> 请调用 mcp__hydroglm__ask_hydroglm，问“请只回复连接正常。”

查看工具调用记录和实际返回正文。如返回 `session_id`，可以用它延续咨询。自检脚本只检查本地文件和密钥是否已配置，在线连通性以实际工具调用为准。

如果已用旧版 DSH 安装包注册 HydroGLM，现有配置可继续使用。要迁移到本仓库，先备份配置，移除旧的 MCP 注册行及其配置（保留其他插件和系统提示），再运行安装器。安装器检测到手工注册时会停下，避免同一 profile 被注册两次。

如需手动合并 YAML，运行 `python3 install_hydroglm_dsh.py --print-patch` 生成片段，合并到对应 profile 的 `cordis.patch.yml`，并将仓库中的 `skills/hydroglm-consult/` 复制到 DSH 用户的 `skills/`。配置指向当前 Python 和 `server.py` 的绝对路径。移动仓库后应重新安装或更新路径。手动配置时，检查 DSH 的实际工具列表和调用记录。

| 现象 | 检查 |
| --- | --- |
| 工具未出现 | 确认修改的是正在使用的 profile，检查 YAML 和 Python 路径，重启 DSH |
| HTTP 401 / 403 | 确认密钥有效且绑定的智能体与工具参数一致 |
| HTTP 429 / 504 或超时 | 稍后重试，必要时运行 `python3 probe_chat.py --agent HydroGLM` 区分上游故障与 DSH 配置问题 |
| 手动调用成功，但普通专业提问没有调用 | 检查技能是否加载，再查看真实工具记录和 [场景验收清单](../skills/hydroglm-consult/references/trigger-validation.md) |

DSH 的 profile 与补丁加载方式见 [DeepSeek Harness 官方架构文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.zh.md)。

## 3. 添加为聊天模型（可选）

这条入口用于直接问答。MCP 已经可以单独用于工程任务。

在 DSH 桌面版打开「设置 → 模型 → 自定义提供商」，填入以下信息，保存后在新会话中选择 HydroGLM。

| 项目 | 填写内容 |
| --- | --- |
| Provider ID | 自定义且不重复，例如 `hanhai` |
| 显示名称 | Hanhai HydroGLM |
| API 地址 | `https://hanhai-ai.com/api/v1/agent/agent/openai` |
| API 协议 | OpenAI Chat Completions |
| API 密钥 | 对应模型的瀚海 API Key |
| 模型 ID | `hydroglm`，或使用对应密钥的 `hydroglm-plus` |

按原桌面安装指南的测试，直接聊天入口只返回文本，文件和命令操作仍走主模型的工具。API 地址应以 `/openai` 结束，聊天客户端会自行拼接 `/chat/completions`。

通过 MCP 发出的咨询问题会发送到瀚海 API。重要公式、参数和工程结论应独立复核。
