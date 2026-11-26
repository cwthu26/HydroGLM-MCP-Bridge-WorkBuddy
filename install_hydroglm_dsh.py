#!/usr/bin/env python3
"""Register HydroGLM MCP and install its consultation skill for DeepSeek Harness."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from generate_config import TOOL_TIMEOUT_SECONDS


ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "server.py"
SKILL = Path("skills/hydroglm-consult")
SKILL_FILES = ("SKILL.md", "references/mcp-setup.md", "references/trigger-validation.md")
BEGIN = "# BEGIN HydroGLM MCP Bridge"
END = "# END HydroGLM MCP Bridge"
MANAGED = re.compile(rf"^{BEGIN}\n.*?^{END}$", re.M | re.S)
LEGACY = re.compile(r"(?:mcp-hydroglm\b|serverName[\"']?\s*:\s*[\"']?hydroglm\b)")


def add_profile_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", default=os.environ.get("DSH_PROFILE") or "desktop",
                        help="DSH profile (default: DSH_PROFILE or desktop)")
    parser.add_argument("--dsh-home", type=Path,
                        default=Path(os.environ.get("DSH_HOME") or Path.home() / ".dsh"),
                        help="DSH data directory (default: DSH_HOME or ~/.dsh)")


def profile_path(home: Path, profile: str) -> Path:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", profile):
        raise ValueError("Invalid DSH profile name")
    return home / "profiles" / profile / "cordis.patch.yml"


def build_patch() -> str:
    command = json.dumps(sys.executable, ensure_ascii=False)
    args = json.dumps(["-X", "utf8", str(SERVER)], ensure_ascii=False)
    cwd = json.dumps(str(ROOT), ensure_ascii=False)
    return (
        f"{BEGIN}\n"
        "- insert:\n"
        "    - id: mcp-hydroglm\n"
        '      name: "@deepseek-ai/dsh-mcp-client"\n'
        "      config:\n"
        "        serverName: hydroglm\n"
        "        transport: stdio\n"
        f"        command: {command}\n"
        f"        args: {args}\n"
        f"        cwd: {cwd}\n"
        f"        toolCallTimeoutMs: {TOOL_TIMEOUT_SECONDS * 1000}\n"
        f"{END}"
    )


def merge_patch(text: str) -> str:
    matches = list(MANAGED.finditer(text))
    if text.count(BEGIN) != len(matches) or text.count(END) != len(matches) or len(matches) > 1:
        raise ValueError("The managed HydroGLM block is incomplete or duplicated")
    if LEGACY.search(MANAGED.sub("", text)):
        raise ValueError("An unmanaged HydroGLM registration already exists. "
                         "Move it out of this patch before installing, or keep using it.")
    if matches:
        return MANAGED.sub(lambda _: build_patch(), text)

    lines = text.splitlines(keepends=True)
    content = [i for i, line in enumerate(lines)
               if line.strip() and not line.lstrip().startswith("#")]
    if content and lines[content[0]].strip() == "---":
        content.pop(0)
    if any(re.match(r"^(?:---|\.\.\.)(?:\s|$)", lines[i]) for i in content):
        raise ValueError("Use --print-patch and merge manually into this YAML document.")
    if len(content) == 1 and re.fullmatch(r"\[\s*\]\s*(?:#.*)?", lines[content[0]].strip()):
        line = lines[content[0]]
        _, comment, remainder = line.partition("#")
        lines[content[0]] = comment + remainder if comment else ""
        text = "".join(lines)
    elif content and not re.match(r"^-(?:\s|$)", lines[content[0]]):
        raise ValueError("Use --print-patch and merge manually into this non-block YAML list.")
    if text and not text.endswith("\n"):
        text += "\n"
    return text + build_patch() + "\n"


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(dir=path.parent)
    name = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as temporary:
            temporary.write(data)
        if path.exists():
            shutil.copymode(path, name)
        os.replace(name, path)
    finally:
        name.unlink(missing_ok=True)


def write_with_backup(path: Path, data: bytes) -> None:
    if path.exists():
        previous = path.read_bytes()
        if previous == data:
            return
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f"{path.name}.bak-",
                                         delete=False) as backup:
            backup.write(previous)
        print(f"Backup: {backup.name}")
    write_atomic(path, data)
    print(f"Updated: {path}")


def install(home: Path, profile: str) -> None:
    config = profile_path(home, profile)
    old_bytes = config.read_bytes() if config.is_file() else b""
    old_text = old_bytes.decode("utf-8-sig")
    new_text = merge_patch(old_text.replace("\r\n", "\n"))
    managed_text = new_text.replace("\n", "\r\n") if b"\r\n" in old_bytes else new_text
    encoding = "utf-8-sig" if old_bytes.startswith(b"\xef\xbb\xbf") else "utf-8"
    skill_files = {name: (ROOT / SKILL / name).read_bytes() for name in SKILL_FILES}

    shared = home / "cordis.patch.yml"
    if shared.is_file() and LEGACY.search(shared.read_text(encoding="utf-8-sig")):
        raise ValueError(f"Remove or reuse the existing HydroGLM registration in {shared}.")
    write_with_backup(config, managed_text.encode(encoding))
    for name, data in skill_files.items():
        write_with_backup(home / SKILL / name, data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_profile_args(parser)
    parser.add_argument("--print-patch", action="store_true",
                        help="Print a DSH patch without changing your profile or skills")
    args = parser.parse_args()
    try:
        if not SERVER.is_file():
            raise ValueError(f"MCP server does not exist: {SERVER}")
        if args.print_patch:
            print(build_patch())
        else:
            install(args.dsh_home.expanduser(), args.profile)
            print(f"Restart DSH using profile {args.profile!r} and open a new session.")
    except (OSError, ValueError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
