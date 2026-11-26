#!/usr/bin/env python3
"""Check the local DeepSeek Harness installation without sending an API request."""

from __future__ import annotations

import argparse
import sys

from install_hydroglm_dsh import MANAGED, ROOT, SERVER, SKILL, SKILL_FILES
from install_hydroglm_dsh import add_profile_args, build_patch, profile_path
from server import AGENTS, read_api_key


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_profile_args(parser)
    parser.add_argument("--agent", choices=AGENTS, default="HydroGLM")
    args = parser.parse_args()
    home = args.dsh_home.expanduser()
    try:
        config = profile_path(home, args.profile)
        text = config.read_text(encoding="utf-8-sig") if config.is_file() else ""
        managed = MANAGED.findall(text)
        skill_ready = all(
            (home / SKILL / name).is_file()
            and (home / SKILL / name).read_bytes() == (ROOT / SKILL / name).read_bytes()
            for name in SKILL_FILES
        )
    except (OSError, ValueError) as exc:
        print(f"Check failed: {exc}", file=sys.stderr)
        return 1
    try:
        read_api_key(args.agent)
        has_key = True
    except RuntimeError:
        has_key = False

    checks = (
        (sys.version_info >= (3, 10), "Python 3.10+"),
        (SERVER.is_file(), f"MCP bridge: {SERVER}"),
        (managed == [build_patch()], f"Managed MCP block in {config}"),
        (skill_ready, f"Consultation skill: {home / SKILL}"),
        (has_key, f"Local API key configured for {args.agent}"),
    )
    for passed, description in checks:
        print(f"[{'OK' if passed else 'CHECK'}] {description}")
    print("For a live check, call mcp__hydroglm__ask_hydroglm in a new DSH session.")
    return 0 if all(passed for passed, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
