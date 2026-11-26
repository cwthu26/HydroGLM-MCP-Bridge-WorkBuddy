#!/usr/bin/env python3
"""Build an allow-listed source ZIP; never package user credentials or configs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile

from server import SERVER_VERSION

ROOT = Path(__file__).resolve().parent
ROOT_FILES = (
    "README.md", "RELEASE_NOTES.md", "CHANGELOG.md", "LICENSE", "SECURITY.md",
    ".gitignore", "server.py", "configure_key.py", "generate_config.py",
    "diagnose.py", "probe_chat.py", "build_release.py", ".github/workflows/tests.yml",
    "install_hydroglm_dsh.py", "verify_hydroglm_dsh.py",
    "package.json", "package-lock.json",
)
PATTERNS = ("docs/*.md", "examples/*.json", "examples/*.toml", "tests/test_*.py",
            "skills/hydroglm-consult/*.md", "skills/hydroglm-consult/references/*.md",
            "bin/*.cjs", "scripts/*.cjs", "tests/*.test.cjs")
LONG_KEY = re.compile(rb"\bsk-[A-Za-z0-9_-]{32,}\b")
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")


def release_files(root: Path = ROOT) -> list[Path]:
    paths = {root / name for name in ROOT_FILES}
    for pattern in PATTERNS:
        paths.update(root.glob(pattern))
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing file or symlink is not allowed: {path.relative_to(root)}")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def validate_content(relative: str, data: bytes, root: Path = ROOT) -> None:
    # Only report the file name, never the matching secret or line.
    private_key_marker = b"-----BEGIN " + b"PRIVATE KEY-----"
    if LONG_KEY.search(data) or private_key_marker in data:
        raise ValueError(f"Possible credential found: {relative}")
    if str(root).encode("utf-8") in data:
        raise ValueError(f"Local project path found: {relative}")


def check_markdown(path: Path, text: str, root: Path = ROOT,
                   included: set[str] | None = None) -> None:
    if sum(line.lstrip().startswith("```") for line in text.splitlines()) % 2:
        raise ValueError(f"Unclosed code fence: {path.relative_to(root)}")
    for raw in LINK.findall(text):
        target = raw.strip().split(' "', 1)[0].strip("<>")
        parts = urlsplit(target)
        if parts.scheme or not parts.path:
            continue
        resolved = (path.parent / unquote(parts.path)).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
            raise ValueError(f"Broken local link in {path.relative_to(root)}: {target}")
        relative = resolved.relative_to(root.resolve()).as_posix()
        if included is not None and relative not in included:
            raise ValueError(f"Link target is not included in release: {relative}")


def build(output_dir: Path) -> dict:
    files = release_files()
    included = {path.relative_to(ROOT).as_posix() for path in files}
    contents = {}
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        validate_content(relative, data)
        if path.suffix == ".md":
            check_markdown(path, data.decode("utf-8"), included=included)
        contents[relative] = data

    output_dir.mkdir(parents=True, exist_ok=True)
    basename = f"HydroGLM-MCP-Bridge-v{SERVER_VERSION}"
    archive = output_dir / f"{basename}.zip"
    manifest = output_dir / f"{basename}.manifest.json"
    checksum_file = output_dir / f"{basename}.sha256"
    if any(path.exists() for path in (archive, manifest, checksum_file)):
        raise ValueError("Release files already exist; select a new --output-dir")

    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as zipped:
        for relative, data in contents.items():
            info = zipfile.ZipInfo(f"HydroGLM-MCP-Bridge/{relative}")
            info.create_system = 3
            info.external_attr = (0o100755 if relative.startswith("bin/") else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zipped.writestr(info, data)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    report = {
        "version": SERVER_VERSION,
        "archive": archive.name,
        "archive_sha256": checksum,
        "file_count": len(contents),
        "files": [
            {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in contents.items()
        ],
    }
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checksum_file.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        report = build(args.output_dir.resolve())
    except (OSError, ValueError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({key: value for key, value in report.items() if key != "files"},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
