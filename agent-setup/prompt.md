# Set up HydroGLM MCP Bridge

Install HydroGLM MCP Bridge for the AI client the user is using. This project runs a local Python stdio MCP server that exposes `ask_hydroglm`. Set up the bridge on the same machine and user account as the client. Use only the filesystem and client configuration the user has authorized.

For DeepSeek Harness, use its [installation guide](https://github.com/cwthu26/HydroGLM-MCP-Bridge-WorkBuddy/blob/codex/deepseek-harness/docs/DeepSeek-Harness.md) with the [matching source ZIP](https://github.com/cwthu26/HydroGLM-MCP-Bridge-WorkBuddy/archive/refs/heads/codex/deepseek-harness.zip). The DeepSeek Harness installer configures the selected profile. Use the steps below for Codex, WorkBuddy, Claude Desktop, and other local stdio clients.

## Fetch and verify the release

1. Confirm that the client can run local stdio MCP and that Python 3.10 or newer is available. Resolve the absolute path of the Python interpreter that passes the version check. On Windows, `py -3 -c "import sys; print(sys.executable)"` can find the interpreter.
2. Fetch `manifest.json` beside this prompt. For a repository link, open this prompt from the README and resolve the manifest relative to this file. If only the prompt text is available, use [the public manifest](https://raw.githubusercontent.com/LIMING-gloria/HydroGLM-MCP-Bridge/main/agent-setup/manifest.json). Require `schemaVersion` to be `hydroglm.agent-setup.v1`. The `revision` must be a 40-character hexadecimal Git commit ID and `release` a numeric `major.minor.patch` version.
3. Require exactly these four file paths, each once: `server.py`, `generate_config.py`, `configure_key.py` and `diagnose.py`. For each entry, require its URL to equal `https://raw.githubusercontent.com/LIMING-gloria/HydroGLM-MCP-Bridge/<revision>/<path>`. Download the files to a staging directory over HTTPS. Before running any downloaded code, verify the byte length against `sizeBytes` and the lowercase SHA-256 hex digest against `sha256`. Stop if a file cannot be downloaded or verified.
4. Follow any installation-copy preparation linked in the client table below. For a standard installation copy, place the verified files in a durable user-owned directory such as `~/.hydroglm-mcp-bridge/releases/<release>-<first 12 characters of revision>/`, or a directory the user selected. Reuse an installed copy only if every manifest file matches. Preserve any modified copy and report the conflict. Use absolute paths when registering the server.

## Set up credentials and register MCP

5. Use the requested model, defaulting to `HydroGLM`. From the verified directory use Python to check `server.read_api_key(agent)` and report only whether a key is available. Reuse a key already configured for that model. If a key is missing, run `configure_key.py --agent HydroGLM` (or `--agent HydroGLM-plus`) in a private interactive terminal where the user can type it directly. If the current interface cannot offer private input, give the user the exact command to run in their own terminal. Keep keys out of chat, command-line arguments, and client configuration.
6. Run verified `generate_config.py --client <client>` with the resolved interpreter and merge only the generated `hydroglm_bridge` entry into the actual client configuration. Check for an existing entry before writing. Reuse an equivalent entry. If the same name is already configured differently, preserve it and ask before replacing it. Use the client's supported settings editor or a format-aware edit, preserve unrelated settings, and check that the result parses before reloading.

   | Client | Generator option | Configuration |
   | --- | --- | --- |
   | Codex | `--client codex` | Merge the server table, including its timeouts, into the active user `config.toml` (`$CODEX_HOME/config.toml` if set, otherwise `~/.codex/config.toml`). When available, check registration with `codex mcp get hydroglm_bridge`. |
   | Claude Desktop | `--client claude` | Use the local config opened by Settings → Developer → Edit Config, and merge the entry into `mcpServers`. |
   | WorkBuddy | `--client workbuddy` | Use the [WorkBuddy desktop guide](workbuddy.md) for installation-copy preparation, registration, and verification. |
   | Other local stdio clients | `--client generic` | Map the generated absolute command and arguments to the client's documented local MCP settings. |

   If the active client or writable config location cannot be established, provide the generated snippet and identify where user input is needed. If the client supports only remote connectors, report that this bridge requires local stdio. Reload MCP or ask the user to restart the client if required.

## Verify and report

7. Launch the registered command over stdio and send newline-delimited JSON-RPC `initialize` (MCP protocol version `2025-06-18`), `notifications/initialized`, and `tools/list`. Confirm that `serverInfo.version` matches the manifest and that `ask_hydroglm` is listed. Verify that the tool appears in the reloaded client if its tool list is accessible. Report standalone handshake and client discovery separately.
8. With a key available, use the verified `diagnose.py --agent <agent>` to check the Hanhai models endpoint. Keep credentials and raw diagnostic bodies out of the report. If the user requests a live answer check, call `ask_hydroglm` from the configured client with a short public hydrology question and the selected model. This uses one model request.

Report the installed release and path, the configured client, the model, what was observed, and any pending restart, credentials, or verification. Set up only the requested client. Do not run shell pipelines from the network or send local project files to the provider.
