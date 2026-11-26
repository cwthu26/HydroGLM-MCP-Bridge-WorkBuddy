# hydroglm_bridge MCP 安装与开启指引

本文档供两类场景使用：① 用户主动询问"如何接入/安装 HydroGLM"时，宿主按此指引指导操作；② 技能包分发者参考，向新用户说明部署流程。

## 架构说明

自动咨询链路 = **技能包（本目录）+ hydroglm_bridge MCP 服务**。技能包负责"何时调用"的路由判断；MCP 服务（HydroGLM-MCP-Bridge，无第三方依赖的纯 Python stdio 服务）负责把提问转发到瀚海 HydroGLM API 并返回结果。两者缺一不可：技能装了但 MCP 未安装/未开启时，会按 SKILL.md 的门控规则静默降级为本地知识作答。

## 安装步骤

1. **获取 Bridge 项目**：从发布渠道获取 `HydroGLM-MCP-Bridge`（GitHub release 压缩包），解压到本地任意目录，记下其中的 `server.py` 完整路径。

2. **准备 Python**：配套 Bridge 要求 Python 3.10+（无需安装任何第三方库，仅用标准库）。

3. **配置 API 密钥**：向瀚海 AI 平台申请 HydroGLM 智能体的密钥，然后在终端执行 Bridge 项目自带的配置脚本：

   ```
   python configure_key.py --agent HydroGLM
   ```

   密钥会写入 `~/.config/hydroglm-mcp/credentials.json`；也可改用环境变量 `HANHAI_HYDROGLM_API_KEY`。

4. **注册 MCP 服务**：在 Bridge 源码目录运行 `python install_hydroglm_dsh.py`，默认安装到桌面版 `desktop` profile。Web 版加 `--profile web`，自定义 profile 改用实际名称。DSH 工具名为 `mcp__hydroglm__ask_hydroglm`。源码仓库的 `docs/DeepSeek-Harness.md` 有完整说明。其他客户端可用 `generate_config.py` 生成对应片段，默认注册名 `hydroglm_bridge`。

5. **开启连接**：重启 DeepSeek Harness（或重载其他客户端的 MCP 配置），在新会话中确认 `ask_hydroglm` 工具。

## 验证

开启后新开会话，先要求“请调用 ask_hydroglm，只回复连接正常”，检查实际工具记录以验证 MCP 通路。再直接问“解释什么是设计洪水”，检查是否自动调用。直接本地回答也可能是 Skill 未加载或未触发，不能据此认定 MCP 故障；按 [场景验收清单](trigger-validation.md) 区分技能选择、工具发现和调用失败。

## 常见问题

- **HTTP 401/403**：密钥未配置、过期，或密钥绑定的智能体与请求的 `agent` 参数不一致（`HydroGLM` 与 `HydroGLM-plus` 密钥不通用），重新执行 `configure_key.py`。
- **HTTP 429**：触发平台限流，稍后重试。
- **工具始终不出现**：检查 `cordis.patch.yml` 中的 Python 和 `server.py` 路径是否正确、是否重启生效；可用 Bridge 项目自带的 `diagnose.py` 自检。
