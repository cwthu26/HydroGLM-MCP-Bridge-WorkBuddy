# GitHub 发布指南

建议新建独立仓库 **HydroGLM-MCP-Bridge**。旧仓库 **HydroGLM-Codex-MCP** 继续保留，已有用户的安装路径、文档地址和调用方式不变。

## 发布前

本目录是独立的发布源文件目录，没有复制旧项目的 `.git` 历史、个人密钥或本机客户端配置。保留 `LICENSE` 中的原版权声明及 README 的来源链接。

当前发布版本为 **v1.0.1**。正式发布文案见 [RELEASE_NOTES.md](../RELEASE_NOTES.md)。项目首页供快速了解，详细原理见 [MCP 原理与调用场景](MCP原理与调用场景.md)。

先运行本地检查：

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions 已配置 Linux、Windows、macOS 下的 Python 3.10 / 3.12 离线测试。工作流需推送后才会在 GitHub 运行，文档没有将其标为已通过。

## 生成源码发布包

在项目目录运行：

```bash
python3 build_release.py
```

`dist/` 中会生成 ZIP、文件清单和 SHA256 校验文件。已有同版本产物时，指定一个新目录：

```bash
python3 build_release.py --output-dir release-output
```

打包脚本只收集明确列出的源码、文档、示例和测试文件，检查本机项目路径、疑似长密钥和文档本地链接。它不读取个人凭据目录，不包含 `local.*`、缓存或个人客户端设置。构建脚本的检查用于辅助发布整理，不替代对将要公开文件的实际审阅。

## 创建新仓库并上传

在 GitHub 网页新建空仓库 `HydroGLM-MCP-Bridge`，然后在本目录运行以下命令。将远程 URL 中的账号替换成自己的账号：

```bash
git init -b main
git status --short
git add .gitignore README.md RELEASE_NOTES.md CHANGELOG.md LICENSE SECURITY.md server.py configure_key.py generate_config.py diagnose.py probe_chat.py build_release.py docs examples tests .github
git diff --cached --stat
git commit -m "Prepare HydroGLM MCP Bridge v1.0.1"
git remote add origin https://github.com/YOUR_ACCOUNT/HydroGLM-MCP-Bridge.git
git push -u origin main
```

暂存范围不包括 `local.*` 生成文件、个人 `credentials.json` 或完整客户端设置。提交前查看实际文件列表即可。上述命令供发布者执行，本次文件整理没有创建远程仓库、提交或推送。

## 保留两个版本

1. 保留原仓库，原文档和安装方式继续提供。
2. 新仓库使用本通用版 README 和多客户端说明。
3. 如需相互导流，可在旧仓库 README 加一条“跨客户端版本见 HydroGLM-MCP-Bridge”，同时保留原安装章节。旧仓库是否添加链接由维护者决定，本次未修改。
4. 新仓库首次对外发布可创建 `v1.0.1` Release，将 `RELEASE_NOTES.md` 的内容放入说明，并附上本次生成的 ZIP 和 SHA256 文件。后续独立维护两个项目的版本号。

GitHub 源码发布不等于 WorkBuddy 连接器市场审核或 Claude 扩展上架。本项目首先提供可由用户配置的本地 stdio MCP。
