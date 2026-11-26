#!/usr/bin/env python3
"""Generate client configuration without modifying any installed MCP client."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

CLIENTS = ("workbuddy", "claude", "generic", "codex")
DEFAULT_SERVER_NAME = "hydroglm_bridge"
TOOL_TIMEOUT_SECONDS = 660


def build_config(client: str, python: str, server: Path,
                 server_name: str = DEFAULT_SERVER_NAME) -> str:
    if client not in CLIENTS:
        raise ValueError("Unsupported client")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", server_name):
        raise ValueError("Server name may contain only letters, digits, _ and -")
    server = server.expanduser().resolve()
    if not server.is_file():
        raise ValueError(f"MCP server does not exist: {server}")
    args = ["-X", "utf8", str(server)]
    if client == "codex":
        return (
            f"[mcp_servers.{server_name}]\n"
            f"command = {json.dumps(python, ensure_ascii=False)}\n"
            f"args = {json.dumps(args, ensure_ascii=False)}\n"
            "enabled = true\nstartup_timeout_sec = 20\n"
            f"tool_timeout_sec = {TOOL_TIMEOUT_SECONDS}\n"
        )
    settings = {"command": python, "args": args}
    if client == "workbuddy":
        settings = {"type": "stdio", **settings}
    return json.dumps({"mcpServers": {server_name: settings}},
                      ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=CLIENTS, required=True)
    parser.add_argument("--python", default=sys.executable,
                        help="Python executable; defaults to the interpreter running this script")
    parser.add_argument("--server", type=Path, default=Path(__file__).with_name("server.py"))
    parser.add_argument("--server-name", default=DEFAULT_SERVER_NAME)
    parser.add_argument("--output", type=Path,
                        help="Write a new UTF-8 file instead of printing the snippet")
    parser.add_argument("--force", action="store_true", help="Allow replacing the output file")
    args = parser.parse_args()
    try:
        executable = shutil.which(args.python)
        if executable is None:
            raise ValueError("Python executable not found; pass its absolute path with --python")
        text = build_config(args.client, str(Path(executable).absolute()),
                            args.server, args.server_name)
        if args.output is None:
            print(text, end="")
        else:
            with args.output.open("w" if args.force else "x", encoding="utf-8") as f:
                f.write(text)
            print(f"Wrote configuration snippet: {args.output}")
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
