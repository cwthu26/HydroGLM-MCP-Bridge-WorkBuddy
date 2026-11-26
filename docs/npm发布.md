# npm 发布

包名：`hydroglm-mcp-bridge`，版本：`1.0.1`。本版在 Python 服务外提供 Node.js 启动入口，运行需要 Node.js 22+ 和 Python 3.10+；没有第三方 npm 或 Python 运行时依赖。

## 检查和打包

在项目根目录执行：

```bash
npm test
npm pack --dry-run
npm pack
```

生成 `hydroglm-mcp-bridge-1.0.1.tgz`。`package.json` 使用发布文件白名单，npm 包只包含入口、Python 运行文件、说明和示例，不包含测试、构建脚本、个人密钥、缓存或客户端生成配置。

## 登录并发布

```bash
npm login --registry=https://registry.npmjs.org
npm whoami --registry=https://registry.npmjs.org
npm publish --access public --registry=https://registry.npmjs.org
```

登录在 npm 官方网页完成。发布时按 npm 提示完成账号或二次验证，不要把密码、API Token 或验证码写入项目、命令示例或聊天。

如果直接发布已验证的压缩包，也可在其所在目录执行：

```bash
npm publish ./hydroglm-mcp-bridge-1.0.1.tgz --access public --registry=https://registry.npmjs.org
```

截至 2026-11-20，本次查询未在官方仓库查到该名称的包；实际能否注册以发布时 npm 返回结果为准。当前版本未上传之前，不应将 README 中的 `npx` 命令描述为已上线可用。

## 发布后验证

```bash
npm view hydroglm-mcp-bridge@1.0.1 version --registry=https://registry.npmjs.org
npx -y hydroglm-mcp-bridge@1.0.1 --version
npx -y hydroglm-mcp-bridge@1.0.1 --help
```

再配置客户端并检查 `ask_hydroglm` 工具记录。正常使用直接提问，不需要每次手动指定工具。

## 后续更新

已发布的同名同版本不能再次覆盖。更新时同步修改 `package.json`、`package-lock.json`、`server.py` 中的版本，以及文档和配置示例中的固定版本，再重新验证和发布。若要使用组织或个人 scope，发布前确定实际拥有权限的 `@scope/包名`，并同步更新文档与配置。

官方参考：[发布公共包](https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/)、[package.json 文件清单及命令入口](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/)、[发布认证要求](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification/)。
